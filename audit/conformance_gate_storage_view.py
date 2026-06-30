#!/usr/bin/env python3
"""Conformance gate for exported storage-time views.

Validates the export surface from export_storage_time_view.py:
- allowed fields only
- storage-time order only
- sorted storage timestamps
- storage anchor semantics only
- sticky false fields
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

from export_storage_time_view import export_storage_view  # noqa: E402

ALLOWED_TOP = {
    "storage_time_view_export",
    "read_only",
    "matrix_gated",
    "export_ready",
    "view_type",
    "sort_key",
    "storage_time_only",
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


def validate_export(export: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    extra_top = sorted(set(export.keys()) - ALLOWED_TOP)
    if extra_top:
        errors.append("unauthorized_top_fields:" + ",".join(extra_top))

    required_true = ("storage_time_view_export", "read_only", "matrix_gated", "export_ready", "storage_time_only")
    for key in required_true:
        if export.get(key) is not True:
            errors.append(f"required_true_failed:{key}")

    if export.get("view_type") != "storage_time_sorted_view":
        errors.append("view_type_invalid")
    if export.get("sort_key") != "storage_time_anchor.timestamp_utc":
        errors.append("sort_key_invalid")

    for key in STICKY_FALSE:
        if export.get(key) is not False:
            errors.append(f"sticky_false_failed:top:{key}")

    records = export.get("records")
    if not isinstance(records, list):
        errors.append("records_not_list")
        records = []

    if export.get("record_count") != len(records):
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

    sorted_valid = timestamps == sorted(timestamps)
    if not sorted_valid:
        errors.append("storage_timestamp_sort_invalid")

    gate_passed = not errors
    return {
        "storage_view_external_conformance_gate": True,
        "gate_passed": gate_passed,
        "record_count": len(records),
        "sorted_storage_timestamps_valid": sorted_valid,
        "unauthorized_fields_valid": not any(error.startswith("unauthorized_") for error in errors),
        "anchor_semantics_valid": not any("anchor_" in error for error in errors),
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": errors,
    }


def run_gate(feed_path: Path, repo_root: Path) -> dict[str, Any]:
    export = export_storage_view(feed_path, repo_root)
    if export.get("export_ready") is not True:
        return {
            "storage_view_external_conformance_gate": True,
            "gate_passed": False,
            "record_count": 0,
            "sorted_storage_timestamps_valid": False,
            "unauthorized_fields_valid": False,
            "anchor_semantics_valid": False,
            "authority": False,
            "truth_claim": False,
            "inference_performed": False,
            "state_mutated": False,
            "errors": ["export_not_ready", *export.get("errors", [])],
        }
    return validate_export(export)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run storage view external conformance gate.")
    parser.add_argument("feed", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    result = run_gate(args.feed, args.repo_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["gate_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
