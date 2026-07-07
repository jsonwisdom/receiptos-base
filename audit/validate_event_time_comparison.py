#!/usr/bin/env python3
"""Validate claimed-time comparison v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ALLOWED_TOP = {
    "event_time_comparison",
    "compared",
    "comparison_type",
    "record_count",
    "ordered_records",
    "causation_claim",
    "priority_claim",
    "truth_claim",
    "authority",
    "inference_performed",
    "state_mutated",
    "storage_time_compared",
    "errors",
}

ALLOWED_RECORD = {
    "source_provenance",
    "claimed_timestamp_normalized_utc",
}


def validate_comparison(comparison: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    extra = sorted(set(comparison.keys()) - ALLOWED_TOP)
    if extra:
        errors.append("unauthorized_fields:" + ",".join(extra))

    if comparison.get("event_time_comparison") is not True:
        errors.append("comparison_marker_missing")
    if comparison.get("compared") is not True:
        errors.append("comparison_not_ready")
    if comparison.get("comparison_type") != "claimed_time_order_only":
        errors.append("comparison_type_invalid")

    if comparison.get("causation_claim") is not False:
        errors.append("causation_claim_not_false")
    if comparison.get("priority_claim") is not False:
        errors.append("priority_claim_not_false")
    if comparison.get("truth_claim") is not False:
        errors.append("truth_claim_not_false")
    if comparison.get("authority") is not False:
        errors.append("authority_not_false")
    if comparison.get("inference_performed") is not False:
        errors.append("inference_performed_not_false")
    if comparison.get("state_mutated") is not False:
        errors.append("state_mutated_not_false")
    if comparison.get("storage_time_compared") is not False:
        errors.append("storage_time_compared_not_false")

    ordered = comparison.get("ordered_records")
    if not isinstance(ordered, list):
        errors.append("ordered_records_not_list")
        ordered = []
    if comparison.get("record_count") != len(ordered):
        errors.append("record_count_mismatch")

    timestamps: list[str] = []
    for index, item in enumerate(ordered, start=1):
        if not isinstance(item, dict):
            errors.append(f"ordered_record_not_object:{index}")
            continue
        extra_record = sorted(set(item.keys()) - ALLOWED_RECORD)
        if extra_record:
            errors.append(f"unauthorized_record_fields:{index}:" + ",".join(extra_record))
        ts = item.get("claimed_timestamp_normalized_utc")
        if not isinstance(ts, str) or not ts.endswith("Z"):
            errors.append(f"claimed_timestamp_invalid:{index}")
        else:
            timestamps.append(ts)

    if timestamps != sorted(timestamps):
        errors.append("claimed_time_order_invalid")

    valid = not errors
    return {
        "event_time_comparison_validator": True,
        "comparison_valid": valid,
        "comparison_type_valid": "comparison_type_invalid" not in errors,
        "no_causation_claim": "causation_claim_not_false" not in errors,
        "no_priority_claim": "priority_claim_not_false" not in errors,
        "no_truth_claim": "truth_claim_not_false" not in errors,
        "no_authority": "authority_not_false" not in errors,
        "no_storage_time_comparison": "storage_time_compared_not_false" not in errors,
        "claimed_order_valid": "claimed_time_order_invalid" not in errors,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate claimed-time comparison v0.")
    parser.add_argument("comparison", type=Path)
    args = parser.parse_args()

    comparison = json.loads(args.comparison.read_text(encoding="utf-8"))
    result = validate_comparison(comparison)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["comparison_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
