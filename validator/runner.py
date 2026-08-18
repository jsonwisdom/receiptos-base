"""Fixture runner for the M7 Validator Harness.

Loads positive and negative fixtures, executes the invariant suite, and emits
deterministic PASS / FAIL_LEG_VIOLATION outcomes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .graph import LEGGraph
from .invariants import InvariantResult, InvariantSuite
from .authorization import AuthorizationReceiptValidator


class HarnessRunner:
    def __init__(self, fixtures_root: Path) -> None:
        self.fixtures_root = fixtures_root
        self.suite = InvariantSuite()
        self.auth_validator = AuthorizationReceiptValidator()

    def run_fixture(self, fixture_path: Path) -> Dict[str, Any]:
        data = json.loads(fixture_path.read_text(encoding="utf-8"))
        expected_violation: Optional[str] = data.get("expected_violation")

        graph = LEGGraph()
        # Support both pure graph fixtures and mixed fixtures
        if "nodes" in data:
            graph.load_from_dict(data)

        # Collect any embedded AuthorizationReceipts
        auth_receipts: Dict[str, Dict[str, Any]] = {}
        if "authorization_receipt" in data:
            rec = data["authorization_receipt"]
            auth_receipts[rec.get("receipt_id", "embedded")] = rec
        # Also accept a top-level receipt that looks like AuthorizationReceipt
        if all(k in data for k in ("receipt_id", "subject_decision_id", "authorization_type")):
            auth_receipts[data["receipt_id"]] = data

        results = self.suite.check_all(graph, auth_receipts)

        failed = [r for r in results if not r.passed]
        outcome = "PASS" if not failed else "FAIL_LEG_VIOLATION"

        # For negative fixtures, success means we detected the expected violation
        if expected_violation:
            detected = any(r.code == expected_violation and not r.passed for r in results)
            if detected:
                outcome = "PASS"  # correctly rejected
            else:
                outcome = "FAIL_LEG_VIOLATION"  # missed the expected violation

        return {
            "fixture": str(fixture_path),
            "outcome": outcome,
            "expected_violation": expected_violation,
            "results": [
                {"code": r.code, "passed": r.passed, "detail": r.detail} for r in results
            ],
        }

    def run_all(self) -> List[Dict[str, Any]]:
        results = []
        for sub in ("valid", "invalid"):
            d = self.fixtures_root / sub
            if not d.is_dir():
                continue
            for p in sorted(d.glob("*.json")):
                results.append(self.run_fixture(p))
        return results


def main(argv: Optional[List[str]] = None) -> int:
    argv = argv or sys.argv[1:]
    root = Path(argv[0]) if argv else Path("fixtures/m7")
    runner = HarnessRunner(root)
    outcomes = runner.run_all()

    failed = [o for o in outcomes if o["outcome"] != "PASS"]
    for o in outcomes:
        print(f"{o['outcome']:20} {o['fixture']}")
        if o["outcome"] != "PASS":
            for r in o["results"]:
                if not r["passed"]:
                    print(f"  → {r['code']}: {r['detail']}")

    print(f"\n{len(outcomes) - len(failed)}/{len(outcomes)} fixtures passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
