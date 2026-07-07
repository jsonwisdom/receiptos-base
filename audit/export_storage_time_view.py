#!/usr/bin/env python3
"""Read-only exporter for storage-time sorted views.

Builds the storage-time view, runs the storage-view matrix, and exports only
ready storage-time records. Storage time is presentation order only.
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

from storage_time_view import build_view  # noqa: E402
from storage_view_conformance_matrix import run_matrix  # noqa: E402


def export_storage_view(feed_path: Path, repo_root: Path) -> dict[str, Any]:
    matrix = run_matrix(repo_root)
    if matrix.get("matrix_passed") is not True:
        return {
            "storage_time_view_export": True,
            "read_only": True,
            "matrix_gated": True,
            "export_ready": False,
            "records": [],
            "authority": False,
            "truth_claim": False,
            "inference_performed": False,
            "state_mutated": False,
            "errors": ["storage_view_matrix_failed", *matrix.get("errors", [])],
        }

    feed = json.loads(feed_path.read_text(encoding="utf-8"))
    view = build_view(feed, str(feed_path))
    if view.get("view_ready") is not True:
        return {
            "storage_time_view_export": True,
            "read_only": True,
            "matrix_gated": True,
            "export_ready": False,
            "records": [],
            "authority": False,
            "truth_claim": False,
            "inference_performed": False,
            "state_mutated": False,
            "errors": ["storage_view_not_ready", *view.get("errors", [])],
        }

    records = []
    for item in view.get("records", []):
        records.append({
            "entry_id": item.get("entry_id"),
            "entry_sequence": item.get("entry_sequence"),
            "sequence_semantics": "storage_order_only",
            "batch_root": item.get("batch_root"),
            "storage_timestamp_utc": item.get("storage_timestamp_utc"),
            "anchor_type": item.get("anchor_type"),
            "anchor_semantics": item.get("anchor_semantics"),
            "authority": False,
            "truth_claim": False,
            "inference_performed": False,
            "state_mutated": False,
        })

    return {
        "storage_time_view_export": True,
        "read_only": True,
        "matrix_gated": True,
        "export_ready": True,
        "view_type": "storage_time_sorted_view",
        "sort_key": "storage_time_anchor.timestamp_utc",
        "storage_time_only": True,
        "record_count": len(records),
        "records": records,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a matrix-gated storage-time view.")
    parser.add_argument("feed", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    result = export_storage_view(args.feed, args.repo_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["export_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
