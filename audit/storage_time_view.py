#!/usr/bin/env python3
"""Storage-time sorted view over validated anchor feeds."""

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

from validate_subscription_feed import validate_feed  # noqa: E402


def build_view(feed: dict[str, Any], source: str) -> dict[str, Any]:
    check = validate_feed(feed, source)
    if check.get("feed_valid") is not True:
        return {
            "timeline_semantics_v0": True,
            "view_type": "storage_time_sorted_view",
            "view_ready": False,
            "storage_time_only": True,
            "sort_key": "storage_time_anchor.timestamp_utc",
            "records": [],
            "authority": False,
            "truth_claim": False,
            "inference_performed": False,
            "state_mutated": False,
            "errors": ["feed_validation_failed", *check.get("errors", [])],
        }

    records: list[dict[str, Any]] = []
    for entry in feed.get("entries", []):
        anchor = entry.get("storage_time_anchor")
        if not anchor:
            continue
        records.append({
            "entry_id": entry.get("entry_id"),
            "entry_sequence": entry.get("entry_sequence"),
            "sequence_semantics": "storage_order_only",
            "batch_root": entry.get("batch_root"),
            "storage_timestamp_utc": anchor.get("timestamp_utc"),
            "anchor_type": anchor.get("anchor_type"),
            "anchor_semantics": anchor.get("semantics"),
            "authority": False,
            "truth_claim": False,
            "inference_performed": False,
            "state_mutated": False,
        })

    records = sorted(records, key=lambda item: item["storage_timestamp_utc"])

    return {
        "timeline_semantics_v0": True,
        "view_type": "storage_time_sorted_view",
        "view_ready": True,
        "storage_time_only": True,
        "sort_key": "storage_time_anchor.timestamp_utc",
        "record_count": len(records),
        "records": records,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build storage-time view from a validated feed.")
    parser.add_argument("feed", type=Path)
    args = parser.parse_args()

    feed = json.loads(args.feed.read_text(encoding="utf-8"))
    result = build_view(feed, str(args.feed))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["view_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
