#!/usr/bin/env python3
"""External subscriber conformance matrix for storage-view feed v0."""

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

from external_subscriber_validator import validate_external_subscriber  # noqa: E402

CASES = [
    {
        "case_id": "positive_subscriber_contract",
        "contract": "audit/fixtures/subscriber-contract-valid.example.json",
        "expected_valid": True,
        "expected_errors": [],
    },
    {
        "case_id": "negative_write_method_contract",
        "contract": "audit/fixtures/subscriber-contract-negative-write.example.json",
        "expected_valid": False,
        "expected_errors": ["subscriber_write_method_allowed"],
    },
    {
        "case_id": "negative_ordering_contract",
        "contract": "audit/fixtures/subscriber-contract-negative-ordering.example.json",
        "expected_valid": False,
        "expected_errors": ["subscriber_cursor_invalid", "subscriber_ordering_invalid"],
    },
]


def run_case(case: dict[str, Any], feed_path: Path, repo_root: Path) -> dict[str, Any]:
    result = validate_external_subscriber(feed_path, repo_root / case["contract"], repo_root)
    errors = result.get("errors", [])
    expected_errors = case["expected_errors"]
    passed = (
        result.get("subscriber_valid") is case["expected_valid"]
        and all(error in errors for error in expected_errors)
    )
    return {
        "case_id": case["case_id"],
        "contract": case["contract"],
        "expected_valid": case["expected_valid"],
        "actual_valid": result.get("subscriber_valid"),
        "expected_errors": expected_errors,
        "actual_errors": errors,
        "case_passed": passed,
    }


def run_matrix(feed_path: Path, repo_root: Path) -> dict[str, Any]:
    cases = [run_case(case, feed_path, repo_root) for case in CASES]
    matrix_passed = all(case["case_passed"] for case in cases)
    return {
        "external_subscriber_conformance_matrix": True,
        "matrix_passed": matrix_passed,
        "case_count": len(cases),
        "positive_count": 1,
        "negative_count": 2,
        "cases": cases,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": [] if matrix_passed else ["external_subscriber_matrix_failed"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run external subscriber conformance matrix.")
    parser.add_argument("feed", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    result = run_matrix(args.feed, args.repo_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["matrix_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
