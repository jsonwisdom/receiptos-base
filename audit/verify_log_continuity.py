#!/usr/bin/env python3
"""Audit log continuity verifier.

Checks JSONL batch-root audit logs for sequence continuity, sticky false
fields, and manifest hash consistency.

Sequence is storage order only. This verifier does not add event-time,
causal, priority, evidentiary, authority, or truth semantics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

STICKY_FALSE = ("authority", "truth_claim", "inference_performed", "state_mutated")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_uri(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"jsonl_decode_error:line_{line_number}:{exc}") from exc
        entries.append(entry)
    return entries


def verify_log(log_path: Path, root: Path) -> dict[str, Any]:
    errors: list[str] = []
    entries = load_jsonl(log_path)
    seen_roots: set[str] = set()

    for index, entry in enumerate(entries, start=1):
        if entry.get("entry_sequence") != index:
            errors.append(f"sequence_gap_or_mismatch:{index}")

        if entry.get("audit_log_append") is not True:
            errors.append(f"entry_not_audit_append:{index}")

        if entry.get("append_sequence_semantics") != "storage_order_only":
            errors.append(f"sequence_semantics_invalid:{index}")

        for key in STICKY_FALSE:
            if entry.get(key) is not False:
                errors.append(f"sticky_false_failed:{index}:{key}")

        batch_root = entry.get("batch_root")
        if not isinstance(batch_root, str) or not batch_root.startswith("sha256:"):
            errors.append(f"batch_root_invalid:{index}")
        elif batch_root in seen_roots:
            errors.append(f"duplicate_batch_root:{index}")
        else:
            seen_roots.add(batch_root)

        manifest_path_value = entry.get("manifest_path")
        manifest_hash_value = entry.get("manifest_hash")
        if not isinstance(manifest_path_value, str) or not isinstance(manifest_hash_value, str):
            errors.append(f"manifest_reference_invalid:{index}")
            continue

        manifest_path = root / manifest_path_value
        if not manifest_path.exists():
            errors.append(f"manifest_missing:{index}")
            continue

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        computed_manifest_hash = sha256_uri(canonical_json_bytes(manifest))
        if computed_manifest_hash != manifest_hash_value:
            errors.append(f"manifest_hash_mismatch:{index}")

        if manifest.get("merkle_root") != batch_root:
            errors.append(f"manifest_root_mismatch:{index}")

    verified = not errors
    return {
        "audit_log_verifier": True,
        "log_path": str(log_path),
        "entry_count": len(entries),
        "sequence_continuity_valid": verified,
        "manifest_hashes_valid": verified,
        "roots_unique": len(seen_roots) == len(entries),
        "verified": verified,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify batch-root audit log continuity.")
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    result = verify_log(args.log, args.repo_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verified"] else 1


if __name__ == "__main__":
    sys.exit(main())
