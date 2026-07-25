"""Reference DSSE adapter — packages AttestationEnvelope into a DSSE-like JSON document."""

from __future__ import annotations

import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from attestation_adapter import AttestationAdapter
from attestation_schema import AttestationEnvelope, AttestationResult


class DSSEAdapter(AttestationAdapter):
    def __init__(self, key_id: str, output_dir: Optional[Path] = None):
        self.key_id = key_id
        self.output_dir = Path(output_dir) if output_dir else Path("attestations")

    @property
    def name(self) -> str:
        return "dsse"

    def create(self, envelope: AttestationEnvelope) -> AttestationResult:
        try:
            payload = envelope.to_dict()
            if not payload.get("timestamp_utc"):
                payload["timestamp_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            payload_bytes = json.dumps(
                payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode("utf-8")
            payload_b64 = base64.b64encode(payload_bytes).decode("ascii")
            envelope_digest = hashlib.sha256(payload_bytes).hexdigest()

            sig_material = f"{self.key_id}:{envelope_digest}".encode("utf-8")
            signature_b64 = base64.b64encode(hashlib.sha256(sig_material).digest()).decode("ascii")

            dsse = {
                "payloadType": "application/vnd.replayos.attestation+json",
                "payload": payload_b64,
                "signatures": [{"keyid": self.key_id, "sig": signature_b64}],
            }

            self.output_dir.mkdir(parents=True, exist_ok=True)
            out_path = self.output_dir / f"attestation-dsse-{envelope_digest[:12]}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(dsse, f, indent=2)

            return AttestationResult(
                adapter_name=self.name,
                success=True,
                envelope_digest=envelope_digest,
                reference=str(out_path),
                payload=dsse,
            )
        except Exception as e:
            return AttestationResult(
                adapter_name=self.name,
                success=False,
                errors=[f"DSSE packaging failed: {type(e).__name__}: {e}"],
            )
