#!/usr/bin/env python3
"""Umbrella conformance matrix for #42 event-time lane.

Runs the boundary gate, parser-record matrix, and normalized-record matrix.
This must pass before comparison semantics are introduced.
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

from event_time_conformance_gate import validate_manifest  # noqa: E402
from event_time_record_conformance_matrix import run_matrix as run_record_matrix  # noqa: E402
from normalized_event_time_conformance_matrix import run_matrix as run_normalized_matrix  # noqa: E402

BOUNDARY_CASES = [
    {
        "case_id": "boundary_positive_proposal",
        "fixture": "audit/fixtures/event-time-boundary-proposal.example.json",
        "expected_passed": True,
        "expected_errors": [],
    },
    {
        "case_id": "boundary_negative_storage_import",
        "fixture": "audit/fixtures/event-time-boundary-negative-storage-import.example.json",
        "expected_passed": False,
        "expected_errors": ["forbidden_storage_import:audit.storage_time_view"],
    },
    {
        "case_id": "parser_negative_storage_import",
        "fixture": "audit/fixtures/event-time-parser-negative-storage-import.example.json",
        "expected_passed": False,
        "expected_errors": ["forbidden_storage_import:audit.storage_view_subscription_feed"],
    },
]


def run_boundary_case(case: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    manifest = json.loads((repo_root / case["fixture"]).read_text(encoding="utf-8"))
    result = validate_manifest(manifest)
    errors = result.get("errors", [])
    expected_errors = case["expected_errors"]
    passed = (
        result.get("gate_passed") is case["expected_passed"]
        and all(error in errors for error in expected_errors)
    )
    return {
        "case_id": case["case_id"],
        "fixture": case["fixture"],
        "expected_passed": case["expected_passed"],
        "actual_passed": result.get("gate_passed"),
        "expected_errors": expected_errors,
        "actual_errors": errors,
        "case_passed": passed,
    }


def run_matrix(repo_root: Path) -> dict[str, Any]:
    boundary_results = [run_boundary_case(case, repo_root) for case in BOUNDARY_CASES]
    record_matrix = run_record_matrix(repo_root)
    normalized_matrix = run_normalized_matrix(repo_root)

    boundary_passed = all(case["case_passed"] for case in boundary_results)
    record_passed = record_matrix.get("matrix_passed") is True
    normalized_passed = normalized_matrix.get("matrix_passed") is True
    matrix_passed = boundary_passed and record_passed and normalized_passed

    return {
        "event_time_feature_conformance_matrix": True,
        "matrix_passed": matrix_passed,
        "boundary_matrix_passed": boundary_passed,
        "record_matrix_passed": record_passed,
        "normalized_matrix_passed": normalized_passed,
        "boundary_case_count": len(boundary_results),
        "record_case_count": record_matrix.get("case_count"),
        "normalized_case_count": normalized_matrix.get("case_count"),
        "cases": {
            "boundary": boundary_results,
            "record_matrix_summary": {
                "case_count": record_matrix.get("case_count"),
                "positive_count": record_matrix.get("positive_count"),
                "negative_count": record_matrix.get("negative_count"),
                "errors": record_matrix.get("errors", []),
            },
            "normalized_matrix_summary": {
                "case_count": normalized_matrix.get("case_count"),
                "positive_count": normalized_matrix.get("positive_count"),
                "negative_count": normalized_matrix.get("negative_count"),
                "errors": normalized_matrix.get("errors", []),
            },
        },
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": [] if matrix_passed else ["event_time_feature_matrix_failed"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run #42 event-time feature conformance matrix.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    result = run_matrix(args.repo_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["matrix_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
