"""Unit tests for the M7 Validator Harness."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from validator.graph import LEGGraph
from validator.authorization import AuthorizationReceiptValidator
from validator.invariants import InvariantSuite
from validator.runner import HarnessRunner

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "m7"


def test_acyclic_valid_graph():
    data = json.loads((FIXTURES / "valid" / "lock_graph.json").read_text())
    g = LEGGraph()
    g.load_from_dict(data)
    assert g.is_acyclic()


def test_cycle_detected():
    data = json.loads((FIXTURES / "invalid" / "cycle_in_graph.json").read_text())
    g = LEGGraph()
    g.load_from_dict(data)
    assert not g.is_acyclic()


def test_authorization_receipt_valid():
    rec = json.loads((FIXTURES / "valid" / "authorization_receipt.json").read_text())
    ok, errors = AuthorizationReceiptValidator().validate(rec)
    assert ok, errors


def test_m7_001_missing_authorization():
    data = json.loads((FIXTURES / "invalid" / "missing_authorization.json").read_text())
    g = LEGGraph()
    g.load_from_dict(data)
    results = InvariantSuite().check_all(g)
    m7001 = next(r for r in results if r.code == "M7-001")
    assert not m7001.passed


def test_runner_all_fixtures():
    runner = HarnessRunner(FIXTURES)
    outcomes = runner.run_all()
    assert len(outcomes) >= 4
    # All should report PASS (negative fixtures are expected to fail the invariant)
    for o in outcomes:
        assert o["outcome"] == "PASS", o
