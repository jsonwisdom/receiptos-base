#!/usr/bin/env python3
"""Validate storage-view subscription feed v0."""

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

from storage_view_subscription_feed import build_feed  # noqa: E402

ALLOWED_TOP = {
    "storage_view_subscription_feed_v0",
    "read_only",
    "gate_gated",
    "feed_ready",
    "cursor_type",
    "cursor_after",
    "next_cursor",
    "limit",
    "record_count",
    "records",
    "authority",
    "truth_claim",
    "inference_performed",
    "state_mutated",
    "errors",
}

ALLOWED_RECORD = {
    "entry_id",
    "entry_sequence",
    "sequence_semantics",
    "batch_root",
    "storage_timestamp_utc",
    "anchor_type",
    "anchor_semantics",
    "authority",
    "truth_claim",
    "inference_performed",
    "state_mutated",
}

STICKY_FALSE = ("authority", "truth_claim", "inference_performed", "state_mutated")


def validate_feed(feed: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    extra_top = sorted(set(feed.keys()) - ALLOWED_TOP)
    if extra_top:
        errors.append("unauthorized_top_fields:" + ",".join(extra_top))

    for key in ("storage_view_subscription_feed_v0", "read_only", "gate_gated", "feed_ready"):
        if feed.get(key) is not True:
            errors.append(f"required_true_failed:{key}")

    if feed.get("cursor_type") != "storage_timestamp_utc":
        errors.append("cursor_type_invalid")

    for key in STICKY_FALSE:
        if feed.get(key) is not False:
            errors.append(f"sticky_false_failed:top:{key}")

    records = feed.get("records")
    if not isinstance(records, list):
        errors.append("records_not_list")
        records = []

    if feed.get("record_count") != len(records):
        errors.append("record_count_mismatch")

    timestamps: list[str] = []
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            errors.append(f"record_not_object:{index}")
            continue
        extra_record = sorted(set(record.keys()) - ALLOWED_RECORD)
        if extra_record:
            errors.append(f"unauthorized_record_fields:{index}:" + ",".join(extra_record))
        if record.get("sequence_semantics") != "storage_order_only":
            errors.append(f"sequence_semantics_invalid:{index}")
        if record.get("anchor_type") != "storage_time_only":
            errors.append(f"anchor_type_invalid:{index}")
        if record.get("anchor_semantics") != "log_storage_time_only":
            errors.append(f"anchor_semantics_invalid:{index}")
        timestamp = record.get("storage_timestamp_utc")
        if not isinstance(timestamp, str) or "T" not in timestamp or not timestamp.endswith("Z"):
            errors.append(f"storage_timestamp_invalid:{index}")
        else:
            timestamps.append(timestamp)
        for key in STICKY_FALSE:
            if record.get(key) is not False:
                errors.append(f"sticky_false_failed:{index}:{key}")

    if timestamps != sorted(timestamps):
        errors.append("storage_timestamp_sort_invalid")

    passed = not errors
    return {
        "storage_view_subscription_validator": True,
        "feed_valid": passed,
        "record_count": len(records),
        "cursor_valid": "cursor_type_invalid" not in errors,
        "sorted_storage_timestamps_valid": "storage_timestamp_sort_invalid" not in errors,
        "unauthorized_fields_valid": not any(error.startswith("unauthorized_") for error in errors),
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate storage-view subscription feed v0.")
    parser.add_argument("feed", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--cursor-after")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    built = build_feed(args.feed, args.repo_root, args.cursor_after, args.limit)
    result = validate_feed(built)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["feed_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
