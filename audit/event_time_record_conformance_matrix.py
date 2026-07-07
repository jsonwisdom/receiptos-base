#!/usr/bin/env python3
"""EventTimeRecord conformance matrix."""

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

from validate_event_time_record import validate_record  # noqa: E402

CASES = [
    {
        "case_id": "positive_parser_record",
        "fixture": "event_time/fixtures/claimed-time-record.example.json",
        "expected_valid": True,
        "expected_errors": [],
    },
    {
        "case_id": "negative_internal_source",
        "fixture": "event_time/fixtures/event-time-record-negative-source.example.json",
        "expected_valid": False,
        "expected_errors": ["event_time_source_invalid"],
    },
    {
        "case_id": "negative_storage_field_present",
        "fixture": "event_time/fixtures/event-time-record-negative-storage-field.example.json",
        "expected_valid": False,
        "expected_errors": ["unauthorized_fields:storage_timestamp_utc", "storage_field_present:storage_timestamp_utc"],
    },
]


def run_case(case: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    record = json.loads((repo_root / case["fixture"]).read_text(encoding="utf-8"))
    result = validate_record(record)
    errors = result.get("errors", [])
    expected_errors = case["expected_errors"]
    passed = result.get("record_valid") is case["expected_valid"] and all(error in errors for error in expected_errors)
    return {
        "case_id": case["case_id"],
        "fixture": case["fixture"],
        "expected_valid": case["expected_valid"],
        "actual_valid": result.get("record_valid"),
        "expected_errors": expected_errors,
        "actual_errors": errors,
        "case_passed": passed,
    }


def run_matrix(repo_root: Path) -> dict[str, Any]:
    cases = [run_case(case, repo_root) for case in CASES]
    matrix_passed = all(case["case_passed"] for case in cases)
    return {
        "event_time_record_conformance_matrix": True,
        "matrix_passed": matrix_passed,
        "case_count": len(cases),
        "positive_count": 1,
        "negative_count": 2,
        "cases": cases,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": [] if matrix_passed else ["event_time_record_matrix_failed"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run EventTimeRecord conformance matrix.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    result = run_matrix(args.repo_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["matrix_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
