#!/usr/bin/env python3
"""Claimed-time comparison conformance matrix."""

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

from compare_claimed_times import compare_claimed_times  # noqa: E402
from validate_event_time_comparison import validate_comparison  # noqa: E402

CASES = [
    {
        "case_id": "positive_claimed_time_order",
        "fixture": "event_time/fixtures/claimed-time-normalized-records.example.json",
        "mode": "generate",
        "expected_valid": True,
        "expected_errors": [],
    },
    {
        "case_id": "negative_causal_priority_claims",
        "fixture": "event_time/fixtures/claimed-time-comparison-negative-claims.example.json",
        "mode": "validate",
        "expected_valid": False,
        "expected_errors": ["causation_claim_not_false", "priority_claim_not_false"],
    },
    {
        "case_id": "negative_storage_time_compare",
        "fixture": "event_time/fixtures/claimed-time-comparison-negative-storage-compare.example.json",
        "mode": "validate",
        "expected_valid": False,
        "expected_errors": ["storage_time_compared_not_false"],
    },
]


def run_case(case: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    data = json.loads((repo_root / case["fixture"]).read_text(encoding="utf-8"))
    if case["mode"] == "generate":
        comparison = compare_claimed_times(data)
    else:
        comparison = data
    validation = validate_comparison(comparison)
    errors = [*comparison.get("errors", []), *validation.get("errors", [])]
    expected_errors = case["expected_errors"]
    passed = validation.get("comparison_valid") is case["expected_valid"] and all(error in errors for error in expected_errors)
    return {
        "case_id": case["case_id"],
        "fixture": case["fixture"],
        "expected_valid": case["expected_valid"],
        "actual_valid": validation.get("comparison_valid"),
        "expected_errors": expected_errors,
        "actual_errors": errors,
        "case_passed": passed,
    }


def run_matrix(repo_root: Path) -> dict[str, Any]:
    cases = [run_case(case, repo_root) for case in CASES]
    matrix_passed = all(case["case_passed"] for case in cases)
    return {
        "event_time_comparison_conformance_matrix": True,
        "matrix_passed": matrix_passed,
        "case_count": len(cases),
        "positive_count": 1,
        "negative_count": 2,
        "cases": cases,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": [] if matrix_passed else ["event_time_comparison_matrix_failed"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run event-time comparison conformance matrix.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    result = run_matrix(args.repo_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["matrix_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
