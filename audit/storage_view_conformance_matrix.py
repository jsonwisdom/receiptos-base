#!/usr/bin/env python3
"""Conformance matrix for storage-time view."""

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

from storage_time_view import build_view  # noqa: E402

CASES = [
    {
        "case_id": "positive_storage_anchor_feed",
        "fixture": "audit/fixtures/root-subscription-anchor-readiness.example.json",
        "expected_ready": True,
        "expected_record_count": 1,
        "expected_errors": [],
    },
    {
        "case_id": "negative_bad_anchor_format_feed",
        "fixture": "audit/fixtures/negative-anchor-wrong-format.example.json",
        "expected_ready": False,
        "expected_record_count": 0,
        "expected_errors": ["feed_validation_failed", "storage_anchor_timestamp_invalid:1"],
    },
    {
        "case_id": "negative_wrong_anchor_semantics_feed",
        "fixture": "audit/fixtures/negative-anchor-wrong-semantics.example.json",
        "expected_ready": False,
        "expected_record_count": 0,
        "expected_errors": [
            "feed_validation_failed",
            "storage_anchor_type_invalid:1",
            "storage_anchor_semantics_invalid:1",
        ],
    },
]


def run_case(case: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    fixture = repo_root / case["fixture"]
    feed = json.loads(fixture.read_text(encoding="utf-8"))
    result = build_view(feed, case["fixture"])
    errors = result.get("errors", [])
    expected_errors = case["expected_errors"]
    passed = (
        result.get("view_ready") is case["expected_ready"]
        and result.get("record_count", 0) == case["expected_record_count"]
        and all(error in errors for error in expected_errors)
    )
    return {
        "case_id": case["case_id"],
        "fixture": case["fixture"],
        "expected_ready": case["expected_ready"],
        "actual_ready": result.get("view_ready"),
        "expected_record_count": case["expected_record_count"],
        "actual_record_count": result.get("record_count", 0),
        "expected_errors": expected_errors,
        "actual_errors": errors,
        "case_passed": passed,
    }


def run_matrix(repo_root: Path) -> dict[str, Any]:
    cases = [run_case(case, repo_root) for case in CASES]
    matrix_passed = all(case["case_passed"] for case in cases)
    return {
        "storage_view_conformance_matrix": True,
        "matrix_passed": matrix_passed,
        "case_count": len(cases),
        "positive_count": 1,
        "negative_count": 2,
        "cases": cases,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": [] if matrix_passed else ["storage_view_matrix_failed"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run storage view conformance matrix.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    result = run_matrix(args.repo_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["matrix_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
