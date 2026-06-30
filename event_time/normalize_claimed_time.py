#!/usr/bin/env python3
"""Normalize a claimed EventTimeRecord timestamp to UTC v0.

Input must already be an EventTimeRecord shape. This module does not import
storage-time code, compare storage time, sort records, or create truth claims.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STICKY_FALSE = ("authority", "truth_claim", "inference_performed", "state_mutated")


def normalize_claimed_time(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    if record.get("event_time_record") is not True:
        errors.append("event_time_record_marker_missing")
    if record.get("parsed") is not True:
        errors.append("record_not_parsed")
    if record.get("event_time_source") != "external":
        errors.append("event_time_source_invalid")

    raw_value = record.get("claimed_timestamp_raw")
    if not isinstance(raw_value, str) or not raw_value:
        errors.append("claimed_timestamp_raw_missing")

    for key in STICKY_FALSE:
        if record.get(key) is not False:
            errors.append("sticky_false_failed:" + key)

    normalized = None
    if isinstance(raw_value, str) and raw_value:
        try:
            parsed = datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
            normalized = parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        except ValueError:
            errors.append("claimed_timestamp_parse_failed")

    ok = not errors
    return {
        "event_time_record": True,
        "normalized": ok,
        "event_time_source": "external",
        "source_provenance": record.get("source_provenance"),
        "claimed_timestamp_raw": raw_value,
        "claimed_timestamp_normalized_utc": normalized,
        "timezone_normalized": ok,
        "storage_time_compared": False,
        "sorted": False,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize one claimed EventTimeRecord timestamp to UTC.")
    parser.add_argument("record", type=Path)
    args = parser.parse_args()

    record = json.loads(args.record.read_text(encoding="utf-8"))
    result = normalize_claimed_time(record)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["normalized"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
