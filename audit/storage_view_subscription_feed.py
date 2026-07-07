#!/usr/bin/env python3
"""Storage-view subscription feed v0.

Read-only feed built from the gated storage-time view surface.
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

from conformance_gate_storage_view import run_gate  # noqa: E402
from export_storage_time_view import export_storage_view  # noqa: E402


def build_feed(feed_path: Path, repo_root: Path, cursor_after: str | None = None, limit: int | None = None) -> dict[str, Any]:
    gate = run_gate(feed_path, repo_root)
    if gate.get("gate_passed") is not True:
        return {
            "storage_view_subscription_feed_v0": True,
            "read_only": True,
            "gate_gated": True,
            "feed_ready": False,
            "cursor_type": "storage_timestamp_utc",
            "records": [],
            "authority": False,
            "truth_claim": False,
            "inference_performed": False,
            "state_mutated": False,
            "errors": ["storage_view_gate_failed", *gate.get("errors", [])],
        }

    exported = export_storage_view(feed_path, repo_root)
    records = exported.get("records", [])
    if cursor_after:
        records = [item for item in records if item.get("storage_timestamp_utc", "") > cursor_after]
    if limit is not None:
        records = records[:limit]

    next_cursor = records[-1].get("storage_timestamp_utc") if records else None

    return {
        "storage_view_subscription_feed_v0": True,
        "read_only": True,
        "gate_gated": True,
        "feed_ready": True,
        "cursor_type": "storage_timestamp_utc",
        "cursor_after": cursor_after,
        "next_cursor": next_cursor,
        "limit": limit,
        "record_count": len(records),
        "records": records,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build storage-view subscription feed v0.")
    parser.add_argument("feed", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--cursor-after")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    result = build_feed(args.feed, args.repo_root, args.cursor_after, args.limit)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["feed_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
