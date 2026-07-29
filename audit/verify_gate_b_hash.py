#!/usr/bin/env python3
"""Independent hash replay for the OGC-MN-010 Gate B ledger."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SUBJECT_PATH = "open-goblin-courts/mn/OGC-MN-010/remediation/gate-b/gate-b-seal-ledger.yaml"
ASSERTED = "0454df544b36165ba12882571527e57017cb56e996b4cdc28d5fb3e8f13e4c09"
COMMIT = "40ac73742534a0c8baacc865832a3b3a0dda82ce"
BRANCH = "ci/architecture-repair-validator"
OUTPUT_PATH = Path("audit/gate_b_hash_replay_packet.v1.json")


def read_exact_git_bytes() -> bytes:
    """Read the exact blob bytes stored at COMMIT:SUBJECT_PATH."""
    try:
        completed = subprocess.run(
            ["git", "show", f"{COMMIT}:{SUBJECT_PATH}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("git is not installed or not available on PATH") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"unable to read committed artifact: {detail}") from exc
    return completed.stdout


def main() -> int:
    checker = sys.argv[1].strip() if len(sys.argv) == 2 else "PENDING_INDEPENDENT_CHECKER"
    if len(sys.argv) > 2:
        print("Usage: python3 audit/verify_gate_b_hash.py [checker_identity]", file=sys.stderr)
        return 2

    try:
        raw = read_exact_git_bytes()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    digest = hashlib.sha256(raw).hexdigest()
    match = digest == ASSERTED

    packet = {
        "schema": "OGC-HashReplayPacket",
        "schema_version": "1.0",
        "docket": "OGC-MN-010",
        "gate_id": "B",
        "subject": {
            "path": SUBJECT_PATH,
            "commit": COMMIT,
            "branch": BRANCH,
            "asserted_sha256": ASSERTED,
        },
        "replay": {
            "checker": checker,
            "method": "SHA-256 over exact git blob bytes",
            "canonicalization": "raw bytes as stored in git (no re-encoding)",
            "computed_sha256": digest,
            "byte_length": len(raw),
            "match": match,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "notes": "Read with git show COMMIT:PATH.",
        },
        "result": {
            "status": "VERIFIED" if match else "MISMATCH",
            "certificate_eligible": False,
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(packet, indent=2))
    print(f"\n→ wrote {OUTPUT_PATH}")
    return 0 if match else 1


if __name__ == "__main__":
    raise SystemExit(main())
