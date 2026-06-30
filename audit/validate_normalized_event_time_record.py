#!/usr/bin/env python3
"""Validate normalized EventTimeRecord v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

STICKY_FALSE = ("authority", "truth_claim", "inference_performed", "state_mutated")

ALLOWED_FIELDS = {
    "event_time_record",
    "normalized",
    "event_time_source",
    "source_provenance",
    "claimed_timestamp_raw",
    "claimed_timestamp_normalized_utc",
    "timezone_normalized",
    "storage_time_compared",
    "sorted",
    "authority",
    "truth_claim",
    "inference_performed",
    "state_mutated",
    "errors",
}

FORBIDDEN_STORAGE_FIELDS = {
    "storage_timestamp_utc",
    "storage_time_anchor",
    "storage_time_only",
    "storage_sequence",
}


def validate_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    extra = sorted(set(record.keys()) - ALLOWED_FIELDS)
    if extra:
        errors.append("unauthorized_fields:" + ",".join(extra))
    for field in FORBIDDEN_STORAGE_FIELDS:
        if field in record:
            errors.append("storage_field_present:" + field)

    if record.get("event_time_record") is not True:
        errors.append("event_time_record_marker_missing")
    if record.get("normalized") is not True:
        errors.append("record_not_normalized")
    if record.get("event_time_source") != "external":
        errors.append("event_time_source_invalid")
    if record.get("timezone_normalized") is not True:
        errors.append("timezone_normalized_not_true")
    if record.get("storage_time_compared") is not False:
        errors.append("storage_time_compared_not_false")
    if record.get("sorted") is not False:
        errors.append("sorted_not_false")

    normalized = record.get("claimed_timestamp_normalized_utc")
    if not isinstance(normalized, str) or not normalized.endswith("Z"):
        errors.append("normalized_timestamp_invalid")

    for key in STICKY_FALSE:
        if record.get(key) is not False:
            errors.append("sticky_false_failed:" + key)

    valid = not errors
    return {
        "normalized_event_time_record_validator": True,
        "record_valid": valid,
        "event_time_source_valid": "event_time_source_invalid" not in errors,
        "storage_fields_absent": not any(error.startswith("storage_field_present") for error in errors),
        "sticky_fields_valid": not any(error.startswith("sticky_false_failed") for error in errors),
        "storage_comparison_absent": "storage_time_compared_not_false" not in errors,
        "sorting_absent": "sorted_not_false" not in errors,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate normalized EventTimeRecord v0.")
    parser.add_argument("record", type=Path)
    args = parser.parse_args()

    record = json.loads(args.record.read_text(encoding="utf-8"))
    result = validate_record(record)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["record_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
