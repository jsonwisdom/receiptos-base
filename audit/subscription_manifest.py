#!/usr/bin/env python3
"""Subscription manifest for verified audit roots.

Builds a read-only feed from the verified-root exporter.
Storage sequence remains storage order only.
"""

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

from export_verified_roots import export_verified_roots  # noqa: E402


def build_subscription_manifest(log_path: Path, repo_root: Path) -> dict[str, Any]:
    exported = export_verified_roots(log_path, repo_root)
    if exported.get("consumer_ready") is not True:
        return {
            "root_subscription_manifest": True,
            "read_only": True,
            "verifier_gated": True,
            "subscription_ready": False,
            "feed_type": "verified_batch_roots",
            "sequence_semantics": "storage_order_only",
            "subscriber_count": 0,
            "entries": [],
            "authority": False,
            "truth_claim": False,
            "inference_performed": False,
            "state_mutated": False,
            "errors": ["verified_export_not_ready", *exported.get("errors", [])],
        }

    entries: list[dict[str, Any]] = []
    for item in exported.get("exports", []):
        entries.append({
            "entry_id": item.get("entry_id"),
            "entry_sequence": item.get("entry_sequence"),
            "sequence_semantics": "storage_order_only",
            "batch_root": item.get("batch_root"),
            "manifest_path": item.get("manifest_path"),
            "manifest_hash": item.get("manifest_hash"),
            "leaf_count": item.get("leaf_count"),
            "proof_surface": "manifest_path",
            "authority": False,
            "truth_claim": False,
            "inference_performed": False,
            "state_mutated": False,
        })

    return {
        "root_subscription_manifest": True,
        "read_only": True,
        "verifier_gated": True,
        "subscription_ready": True,
        "feed_type": "verified_batch_roots",
        "sequence_semantics": "storage_order_only",
        "subscriber_count": len(entries),
        "entries": entries,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a read-only subscription manifest for verified roots.")
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    result = build_subscription_manifest(args.log, args.repo_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["subscription_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
