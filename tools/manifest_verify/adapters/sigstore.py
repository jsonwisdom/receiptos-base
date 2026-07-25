"""SigstoreAdapter — packages envelope into a Sigstore-style signed bundle (dry-run reference)."""

from __future__ import annotations

import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from attestation_adapter import AttestationAdapter
from attestation_schema import AttestationEnvelope, AttestationResult


class SigstoreAdapter(AttestationAdapter):
    def __init__(
        self,
        identity_provider: str = "github-actions",
        output_dir: Optional[Path] = None,
        dry_run: bool = True,
    ):
        self.identity_provider = identity_provider
        self.output_dir = Path(output_dir) if output_dir else Path("attestations")
        self.dry_run = dry_run

    @property
    def name(self) -> str:
        return "sigstore"

    def create(self, envelope: AttestationEnvelope) -> AttestationResult:
        try:
            payload = envelope.to_dict()
            if not payload.get("timestamp_utc"):
                payload["timestamp_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            payload_bytes = json.dumps(
                payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode("utf-8")
            payload_b64 = base64.b64encode(payload_bytes).decode("ascii")

            sig_input = payload_bytes + f"sigstore:{self.identity_provider}".encode()
            signature_b64 = base64.b64encode(hashlib.sha256(sig_input).digest()).decode("ascii")

            signed_bundle = {
                "mediaType": "application/vnd.dev.sigstore.bundle.v0.3+json",
                "verificationMaterial": {
                    "certificate": {
                        "rawBytes": base64.b64encode(
                            b"-----BEGIN CERTIFICATE-----\n[Simulated Fulcio Certificate]\n-----END CERTIFICATE-----\n"
                        ).decode("ascii")
                    }
                },
                "dsseEnvelope": {
                    "payload": payload_b64,
                    "payloadType": "application/vnd.replayos.attestation.v1+json",
                    "signatures": [{
                        "keyid": f"sigstore:{self.identity_provider}",
                        "sig": signature_b64,
                    }],
                },
            }

            bundle_bytes = json.dumps(
                signed_bundle, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
            envelope_digest = "sha256:" + hashlib.sha256(bundle_bytes).hexdigest()

            self.output_dir.mkdir(parents=True, exist_ok=True)
            short = hashlib.sha256(bundle_bytes).hexdigest()[:12]
            out_path = self.output_dir / f"sigstore-bundle-{short}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(signed_bundle, f, indent=2)

            return AttestationResult(
                adapter_name=self.name,
                success=True,
                envelope_digest=envelope_digest,
                reference=str(out_path),
                payload=signed_bundle,
                metadata={
                    "identity_provider": self.identity_provider,
                    "bundle_version": "0.3",
                    "dry_run": self.dry_run,
                },
            )
        except Exception as e:
            return AttestationResult(
                adapter_name=self.name,
                success=False,
                errors=[f"Sigstore packaging failed: {type(e).__name__}: {e}"],
            )
