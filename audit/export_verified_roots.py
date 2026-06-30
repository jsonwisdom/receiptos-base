#!/usr/bin/env python3
"""Read-only exporter for verified batch-root audit logs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
if str(AUDIT) not in sys.path:
    sys.path.insert(0, str(AUDIT))

from verify_log_continuity import load_jsonl, verify_log  # noqa: E402


def export_verified_roots(log_path: Path, repo_root: Path) -> dict[str, Any]:
    check = verify_log(log_path, repo_root)
    if check.get("verified") is not True:
        return {
            "verified_root_export": True,
            "read_only": True,
            "verifier_gated": True,
            "consumer_ready": False,
            "exports": [],
            "authority": False,
            "truth_claim": False,
            "inference_performed": False,
            "state_mutated": False,
            "errors": ["audit_log_not_verified", *check.get("errors", [])],
        }

    exports = []
    for entry in load_jsonl(log_path):
        exports.append({
            "entry_id": entry.get("entry_id"),
            "entry_sequence": entry.get("entry_sequence"),
            "sequence_semantics": "storage_order_only",
            "batch_root": entry.get("batch_root"),
            "manifest_path": entry.get("manifest_path"),
            "manifest_hash": entry.get("manifest_hash"),
            "leaf_count": entry.get("leaf_count"),
            "source_use_case": entry.get("source_use_case"),
            "authority": False,
            "truth_claim": False,
            "inference_performed": False,
            "state_mutated": False,
        })

    return {
        "verified_root_export": True,
        "read_only": True,
        "verifier_gated": True,
        "consumer_ready": True,
        "log_path": str(log_path),
        "export_count": len(exports),
        "exports": exports,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export verified batch roots from an audit log.")
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    result = export_verified_roots(args.log, args.repo_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["consumer_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
