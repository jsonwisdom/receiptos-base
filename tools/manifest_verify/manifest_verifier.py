"""
ReplayOS ManifestVerifier

Verifies that a release manifest correctly describes and binds its
referenced artifacts.

Authority model:
- The manifest is descriptive, not authoritative.
- Verification checks integrity of the manifest itself and that
  referenced artifacts exist and match their declared digests.
- Protocol semantics are out of scope (handled by the conformance harness).

Collaborators are injected — the verifier does not construct them.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Protocol, Tuple

from integrity import IntegrityCalculator
from manifest_schema import (
    ArtifactCheck,
    ArtifactRef,
    ArtifactVerificationStatus,
    ReleaseManifest,
    VerificationResult,
)
from uri_resolvers import URIResolverRegistry


class IntegrityVerifier(Protocol):
    def verify(
        self,
        data: dict,
        declared_digest: str,
        algorithm: str = "sha256",
    ) -> Tuple[bool, Optional[str]]:
        ...


class ArtifactResolver(Protocol):
    def resolve(
        self,
        ref: ArtifactRef,
        base_dir: Path,
        strict: bool = True,
    ) -> Tuple[ArtifactVerificationStatus, Optional[str]]:
        ...


class ManifestVerificationError(Exception):
    """Raised only for unexpected failures (not ordinary FAIL results)."""
    pass


class ManifestVerifier:
    """
    Composes injected collaborators to produce a VerificationResult.

    Default collaborators are provided for convenience; tests and alternate
    implementations should inject their own.
    """

    def __init__(
        self,
        *,
        strict: bool = True,
        integrity_verifier: Optional[IntegrityVerifier] = None,
        artifact_resolver: Optional[ArtifactResolver] = None,
    ):
        self.strict = strict
        self.integrity = integrity_verifier or IntegrityCalculator()
        self.resolver = artifact_resolver or URIResolverRegistry()

    def verify_manifest(
        self,
        manifest: ReleaseManifest,
        base_dir: Optional[Path] = None,
    ) -> VerificationResult:
        """
        Verify a loaded ReleaseManifest.

        Args:
            manifest: Typed manifest (from ManifestLoader / ReleaseManifest.from_dict).
            base_dir: Directory used to resolve relative file:// URIs.
        """
        errors: List[str] = []
        warnings: List[str] = []
        checks: List[ArtifactCheck] = []

        root = Path(base_dir) if base_dir is not None else Path.cwd()

        # 1. Integrity (canonicalization lives in IntegrityCalculator, not the schema)
        integrity_ok = False
        if manifest.raw is None:
            errors.append("Cannot recompute integrity: original raw dict missing")
        else:
            algorithm = (
                (manifest.integrity.algorithm if manifest.integrity else "sha256")
                or "sha256"
            )
            declared = manifest.integrity.root_digest if manifest.integrity else ""
            integrity_ok, err = self.integrity.verify(
                manifest.raw,
                declared_digest=declared,
                algorithm=algorithm,
            )
            if not integrity_ok and err:
                errors.append(err)

        # 2. Per-artifact checks via injected resolver
        for ref in manifest.all_artifact_refs():
            if not ref.uri:
                status = ArtifactVerificationStatus.FAIL
                msg: Optional[str] = "Artifact reference missing 'uri'"
            else:
                status, msg = self.resolver.resolve(ref, root, strict=self.strict)

            checks.append(ArtifactCheck(uri=ref.uri or "", status=status, message=msg))

            if status == ArtifactVerificationStatus.FAIL and msg:
                errors.append(msg)
            elif (
                status
                in (
                    ArtifactVerificationStatus.NO_DIGEST,
                    ArtifactVerificationStatus.NOT_VERIFIED,
                )
                and msg
            ):
                warnings.append(msg)

        artifacts_ok = all(
            c.status == ArtifactVerificationStatus.PASS for c in checks
        )

        return VerificationResult(
            integrity_ok=integrity_ok,
            artifacts_ok=artifacts_ok,
            errors=tuple(errors),
            warnings=tuple(warnings),
            artifact_checks=tuple(checks),
        )
