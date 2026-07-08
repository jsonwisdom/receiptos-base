import json
from pathlib import Path

import pytest

from receiptos.weld import WeldValidationError, validate_deerflow_weld


FIXTURE_DIR = Path("tests/fixtures/weld")
EXPECTED_OUTPUT_HASH = "sha256:78ab7666760f900e2ab9de6ee5fe09a7620bc27979043ad46bc915ab7c02382e"


def load_fixture(name: str):
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_valid_deerflow_weld_passes_with_deterministic_hash():
    payload = load_fixture("deerflow-valid.json")

    result = validate_deerflow_weld(payload)

    assert result.valid is True
    assert result.authority is False
    assert result.receipt_anchor == "GRP-004-PROMO-20260708-6d405d9e"
    assert result.output_hash == EXPECTED_OUTPUT_HASH


def test_valid_deerflow_weld_is_replay_stable():
    payload = load_fixture("deerflow-valid.json")

    first = validate_deerflow_weld(payload)
    second = validate_deerflow_weld(json.loads(json.dumps(payload)))

    assert first == second


def test_invalid_deerflow_weld_fails_closed():
    payload = load_fixture("deerflow-invalid.json")

    with pytest.raises(WeldValidationError, match="receipt_anchor"):
        validate_deerflow_weld(payload)


def test_authority_escalation_fails_closed():
    payload = load_fixture("deerflow-valid.json")
    payload["authority"] = True

    with pytest.raises(WeldValidationError, match="authority"):
        validate_deerflow_weld(payload)
