#!/usr/bin/env python3
"""Normalized EventTimeRecord conformance matrix."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVENT_TIME = ROOT / "event_time"
if str(EVENT_TIME) not in sys.path:
    sys.path.insert(0, str(EVENT_TIME))

from normalize_claimed_time import normalize_claimed_time  # noqa: E402
from validate_normalized_event_time_record import validate_record  # noqa: E402

CASES = [
    {
        "case_id": "positive_normalized_record",
        "fixture": "event_time/fixtures/claimed-time-record.example.json",
        "expected_normalized": True,
        "expected_valid": True,
        "expected_errors": [],
    },
    {
        "case_id": "negative_malformed_timestamp",
        "fixture": "event_time/fixtures/claimed-time-normalize-negative-malformed.example.json",
        "expected_normalized": False,
        "expected_valid": False,
        "expected_errors": ["claimed_timestamp_parse_failed"],
    },
]


def run_case(case: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    source = json.loads((repo_root / case["fixture"]).read_text(encoding="utf-8"))
    normalized = normalize_claimed_time(source)
    validation = validate_record(normalized)
    errors = [*normalized.get("errors", []), *validation.get("errors", [])]
    expected_errors = case["expected_errors"]
    passed = (
        normalized.get("normalized") is case["expected_normalized"]
        and validation.get("record_valid") is case["expected_valid"]
        and all(error in errors for error in expected_errors)
    )
    return {
        "case_id": case["case_id"],
        "fixture": case["fixture"],
        "expected_normalized": case["expected_normalized"],
        "actual_normalized": normalized.get("normalized"),
        "expected_valid": case["expected_valid"],
        "actual_valid": validation.get("record_valid"),
        "expected_errors": expected_errors,
        "actual_errors": errors,
        "case_passed": passed,
    }


def run_matrix(repo_root: Path) -> dict[str, Any]:
    cases = [run_case(case, repo_root) for case in CASES]
    matrix_passed = all(case["case_passed"] for case in cases)
    return {
        "normalized_event_time_conformance_matrix": True,
        "matrix_passed": matrix_passed,
        "case_count": len(cases),
        "positive_count": 1,
        "negative_count": 1,
        "cases": cases,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": [] if matrix_passed else ["normalized_event_time_matrix_failed"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run normalized EventTimeRecord conformance matrix.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    result = run_matrix(args.repo_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["matrix_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
