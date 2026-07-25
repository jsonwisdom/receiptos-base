"""
CLIOrchestrator — capability registry and pipeline coordination.

The CLI parses args and renders results; this module owns wiring.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from adapters.dsse import DSSEAdapter
from adapters.sigstore import SigstoreAdapter
from anchors.rekor import RekorAnchor
from attestation_manager import AttestationManager
from attestation_schema import (
    AttestationEnvelope,
    AttestationResult,
    SubjectRef,
    VerificationSummary,
)
from gatekeeper import GatekeeperError, enforce_attestation_gate
from manifest_loader import ManifestLoader
from manifest_schema import ReleaseManifest, VerificationResult
from manifest_verifier import ManifestVerifier
from publishers.base import LocalFilesystemPublisher, Publisher


@dataclass
class CapabilityInfo:
    kind: str          # adapter | anchor | publisher | resolver
    name: str
    description: str = ""


@dataclass
class OrchestratorConfig:
    output_dir: Path = field(default_factory=lambda: Path("attestations"))
    signer_id: str = "cli:default"
    strict: bool = True


class CLIOrchestrator:
    """
    Registers capabilities and runs verify / attest / interop pipelines.
    Knows nothing about argparse or stdout formatting.
    """

    def __init__(self, config: Optional[OrchestratorConfig] = None) -> None:
        self.config = config or OrchestratorConfig()
        self.manager = AttestationManager()
        self.anchors: Dict[str, Any] = {}
        self.publishers: Dict[str, Publisher] = {}
        self._resolver_names: List[str] = ["file", "ipfs", "https"]
        self._registered: List[CapabilityInfo] = []

    def register_defaults(self) -> None:
        out = self.config.output_dir
        out.mkdir(parents=True, exist_ok=True)

        self.register_adapter(
            "dsse",
            DSSEAdapter(key_id=self.config.signer_id, output_dir=out),
            description="DSSE-style JSON envelope",
        )
        self.register_adapter(
            "sigstore",
            SigstoreAdapter(
                identity_provider="github-actions",
                output_dir=out,
                dry_run=True,
            ),
            description="Sigstore bundle (dry-run reference)",
        )
        self.register_anchor(
            "rekor",
            RekorAnchor(
                receipt_path=out / "rekor_inclusion_receipt.json",
                dry_run=True,
            ),
            description="Rekor transparency log (dry-run)",
        )
        self.register_publisher(
            "local",
            LocalFilesystemPublisher(dest_dir=out / "published"),
            description="Copy artifacts to local directory",
        )

    def register_adapter(self, name: str, adapter: Any, description: str = "") -> None:
        self.manager.register_adapter(name, adapter)
        self._registered.append(CapabilityInfo("adapter", name, description))

    def register_anchor(self, name: str, anchor: Any, description: str = "") -> None:
        self.anchors[name] = anchor
        self._registered.append(CapabilityInfo("anchor", name, description))

    def register_publisher(self, name: str, publisher: Publisher, description: str = "") -> None:
        self.publishers[name] = publisher
        self._registered.append(CapabilityInfo("publisher", name, description))

    def list_capabilities(self) -> List[CapabilityInfo]:
        caps = list(self._registered)
        for name in self._resolver_names:
            caps.append(CapabilityInfo("resolver", name, f"URI scheme: {name}"))
        return caps

    def verify(
        self,
        manifest_path: Path,
        artifacts_root: Optional[Path] = None,
    ) -> VerificationResult:
        base = artifacts_root or manifest_path.parent
        manifest = ManifestLoader.load(manifest_path)
        return ManifestVerifier(strict=self.config.strict).verify_manifest(
            manifest, base_dir=base
        )

    def attest(
        self,
        manifest_path: Path,
        artifacts_root: Optional[Path] = None,
        adapter_names: Optional[List[str]] = None,
        anchor_names: Optional[List[str]] = None,
    ) -> tuple:
        """Verify → gatekeeper → envelope → adapters → optional anchors."""
        base = artifacts_root or manifest_path.parent
        manifest = ManifestLoader.load(manifest_path)
        vresult = ManifestVerifier(strict=self.config.strict).verify_manifest(
            manifest, base_dir=base
        )

        enforce_attestation_gate(vresult)

        envelope = self._build_envelope(manifest_path, manifest, vresult)

        if adapter_names:
            for name in list(self.manager.registered_adapters):
                if name not in adapter_names:
                    self.manager.unregister_adapter(name)

        results = self.manager.create_attestations(envelope)

        if anchor_names:
            for aname in anchor_names:
                anchor = self.anchors.get(aname)
                if anchor is None:
                    continue
                for res in results:
                    if res.success:
                        anchor.anchor(res)

        return vresult, results

    def interop(self, fixtures_dir: Path) -> Dict[str, Any]:
        """Run normative fixtures and return a canonical parity vector dict."""
        cases = []
        for kind in ("valid", "corrupted"):
            kind_dir = fixtures_dir / kind
            if not kind_dir.exists():
                continue
            for manifest_file in sorted(kind_dir.glob("*/manifest.json")):
                case_name = manifest_file.parent.name
                base_dir = manifest_file.parent
                try:
                    result = self.verify(manifest_file, artifacts_root=base_dir)
                    manifest = ManifestLoader.load(manifest_file)
                    cases.append({
                        "case": case_name,
                        "kind": kind,
                        "valid": result.valid,
                        "integrity_ok": result.integrity_ok,
                        "artifacts_ok": result.artifacts_ok,
                        "root_digest": (
                            manifest.integrity.root_digest
                            if manifest.integrity else None
                        ),
                        "artifact_statuses": [
                            {"uri": c.uri, "status": c.status.value}
                            for c in result.artifact_checks
                        ],
                        "error_count": len(result.errors),
                    })
                except Exception as e:
                    cases.append({
                        "case": case_name,
                        "kind": kind,
                        "valid": False,
                        "error": f"{type(e).__name__}: {e}",
                    })

        return {
            "schema_version": "1.0.0",
            "generator": "replayos-cli/interop",
            "cases": sorted(cases, key=lambda c: c["case"]),
        }

    def _build_envelope(self, manifest_path, manifest, vresult):
        root_digest = ""
        if manifest.integrity and manifest.integrity.root_digest:
            root_digest = f"sha256:{manifest.integrity.root_digest}"
        return AttestationEnvelope(
            schema_version="1.0.0",
            subject=SubjectRef(
                type="replayos_manifest",
                uri=f"file://{manifest_path.name}",
                root_digest=root_digest,
            ),
            verification=VerificationSummary(
                valid=vresult.valid,
                integrity_ok=vresult.integrity_ok,
                artifacts_ok=vresult.artifacts_ok,
                algorithm="sha256",
                error_count=len(vresult.errors),
            ),
            signer_id=self.config.signer_id,
            timestamp_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            metadata={"tool": "replayos-cli", "tool_version": "0.1.0"},
        )
