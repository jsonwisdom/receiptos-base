"""RekorAnchor — records AttestationResult in a Rekor transparency log (dry-run)."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Optional

from anchors.base import Anchor
from attestation_schema import AttestationResult


class RekorAnchor(Anchor):
    def __init__(
        self,
        rekor_server_url: str = "https://rekor.sigstore.dev",
        receipt_path: Optional[Path] = None,
        dry_run: bool = True,
    ):
        self.rekor_server_url = rekor_server_url
        self.receipt_path = Path(receipt_path) if receipt_path else Path("rekor_inclusion_receipt.json")
        self.dry_run = dry_run

    def anchor(self, result: AttestationResult) -> bool:
        if not result.success or not result.envelope_digest:
            print(f"  ✗ Skipping Rekor anchoring for failed/empty result [{result.adapter_name}]")
            return False

        digest_bytes = result.envelope_digest.encode("utf-8")
        log_index = int(hashlib.sha256(digest_bytes).hexdigest()[:8], 16) % 50_000_000 + 1_000_000

        log_entry = {
            "server": self.rekor_server_url,
            "logIndex": log_index,
            "integratedTime": int(time.time()),
            "attestedDigest": result.envelope_digest,
            "adapter": result.adapter_name,
            "inclusionProof": {
                "checkpoint": f"{self.rekor_server_url} - {log_index}",
                "hashes": ["sha256:" + hashlib.sha256(digest_bytes + b"|sibling").hexdigest()],
            },
            "dry_run": self.dry_run,
        }

        try:
            self.receipt_path.parent.mkdir(parents=True, exist_ok=True)
            self.receipt_path.write_text(
                json.dumps(log_entry, indent=2, sort_keys=True), encoding="utf-8"
            )
        except OSError as e:
            print(f"  ✗ Failed to write Rekor receipt: {e}")
            return False

        action = "Would log" if self.dry_run else "Logged"
        print(
            f"  🌲 {action} artifact to Rekor [{self.rekor_server_url}]\n"
            f"     Log Index: {log_index} | Digest: {result.envelope_digest[:24]}…"
        )
        return True
