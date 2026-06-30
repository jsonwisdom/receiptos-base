#!/usr/bin/env python3
"""Compare normalized claimed event-time records v0.

Produces claimed-time order only. No causation, priority, truth, or storage-time
comparison is introduced.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

STICKY_FALSE = ("authority", "truth_claim", "inference_performed", "state_mutated")


def _parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def compare_claimed_times(records: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    normalized_records: list[dict[str, Any]] = []

    if not isinstance(records, list) or len(records) < 2:
        errors.append("at_least_two_records_required")
        records = []

    for index, record in enumerate(records):
        if record.get("event_time_record") is not True:
            errors.append(f"event_time_record_marker_missing:{index}")
        if record.get("normalized") is not True:
            errors.append(f"record_not_normalized:{index}")
        if record.get("event_time_source") != "external":
            errors.append(f"event_time_source_invalid:{index}")
        if record.get("storage_time_compared") is not False:
            errors.append(f"storage_time_compared_not_false:{index}")
        for key in STICKY_FALSE:
            if record.get(key) is not False:
                errors.append(f"sticky_false_failed:{index}:{key}")
        timestamp = record.get("claimed_timestamp_normalized_utc")
        if not isinstance(timestamp, str) or not timestamp.endswith("Z"):
            errors.append(f"normalized_timestamp_invalid:{index}")
        else:
            try:
                _parse_utc(timestamp)
            except ValueError:
                errors.append(f"normalized_timestamp_parse_failed:{index}")
        normalized_records.append(record)

    ordered: list[dict[str, Any]] = []
    if not errors:
        ordered = sorted(
            [
                {
                    "source_provenance": item.get("source_provenance"),
                    "claimed_timestamp_normalized_utc": item.get("claimed_timestamp_normalized_utc"),
                }
                for item in normalized_records
            ],
            key=lambda item: item["claimed_timestamp_normalized_utc"],
        )

    return {
        "event_time_comparison": True,
        "compared": not errors,
        "comparison_type": "claimed_time_order_only",
        "record_count": len(records),
        "ordered_records": ordered,
        "causation_claim": False,
        "priority_claim": False,
        "truth_claim": False,
        "authority": False,
        "inference_performed": False,
        "state_mutated": False,
        "storage_time_compared": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare normalized claimed event-time records.")
    parser.add_argument("records", type=Path)
    args = parser.parse_args()

    records = json.loads(args.records.read_text(encoding="utf-8"))
    result = compare_claimed_times(records)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["compared"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
