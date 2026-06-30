#!/usr/bin/env python3
"""Anchor readiness conformance matrix.

Runs positive and negative subscription-feed fixtures through the validator
and reports expected pass/fail behavior in one JSON artifact.
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

from validate_subscription_feed import validate_feed  # noqa: E402

DEFAULT_CASES = [
    {
        "case_id": "positive_storage_time_anchor",
        "fixture": "audit/fixtures/root-subscription-anchor-readiness.example.json",
        "expected_valid": True,
        "expected_errors": [],
    },
    {
        "case_id": "negative_wrong_timestamp_format",
        "fixture": "audit/fixtures/negative-anchor-wrong-format.example.json",
        "expected_valid": False,
        "expected_errors": ["storage_anchor_timestamp_invalid:1"],
    },
    {
        "case_id": "negative_wrong_anchor_semantics",
        "fixture": "audit/fixtures/negative-anchor-wrong-semantics.example.json",
        "expected_valid": False,
        "expected_errors": [
            "storage_anchor_type_invalid:1",
            "storage_anchor_semantics_invalid:1",
        ],
    },
    {
        "case_id": "negative_extra_anchor_field",
        "fixture": "audit/fixtures/negative-anchor-extra-field.example.json",
        "expected_valid": False,
        "expected_errors": ["storage_anchor_extra_fields:1:timeline_rank"],
    },
]


def run_case(case: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    fixture_path = repo_root / case["fixture"]
    feed = json.loads(fixture_path.read_text(encoding="utf-8"))
    result = validate_feed(feed, case["fixture"])
    errors = result.get("errors", [])
    expected_errors = case.get("expected_errors", [])
    expected_valid = case.get("expected_valid")

    validity_matches = result.get("feed_valid") is expected_valid
    expected_errors_present = all(error in errors for error in expected_errors)
    unexpected_pass = expected_valid is False and result.get("feed_valid") is True
    passed = validity_matches and expected_errors_present and not unexpected_pass

    return {
        "case_id": case["case_id"],
        "fixture": case["fixture"],
        "expected_valid": expected_valid,
        "actual_valid": result.get("feed_valid"),
        "expected_errors": expected_errors,
        "actual_errors": errors,
        "case_passed": passed,
    }


def run_matrix(repo_root: Path) -> dict[str, Any]:
    case_results = [run_case(case, repo_root) for case in DEFAULT_CASES]
    matrix_passed = all(case["case_passed"] for case in case_results)
    return {
        "anchor_conformance_matrix": True,
        "matrix_passed": matrix_passed,
        "case_count": len(case_results),
        "positive_count": sum(1 for case in DEFAULT_CASES if case["expected_valid"] is True),
        "negative_count": sum(1 for case in DEFAULT_CASES if case["expected_valid"] is False),
        "cases": case_results,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": [] if matrix_passed else ["anchor_conformance_matrix_failed"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run anchor readiness conformance matrix.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    result = run_matrix(args.repo_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["matrix_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
