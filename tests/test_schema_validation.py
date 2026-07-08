import json
from pathlib import Path

import pytest

try:
    from jsonschema import ValidationError, validate
except ImportError as exc:  # pragma: no cover
    pytest.skip(f"jsonschema unavailable: {exc}", allow_module_level=True)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "receipt_card_v0.2.json"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "card_001_seed.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_card_001_seed_validates_against_receipt_card_schema():
    schema = load_json(SCHEMA_PATH)
    fixture = load_json(FIXTURE_PATH)

    validate(instance=fixture, schema=schema)


def test_authority_true_rejected_by_schema():
    schema = load_json(SCHEMA_PATH)
    fixture = load_json(FIXTURE_PATH)
    fixture["authority"] = True

    with pytest.raises(ValidationError):
        validate(instance=fixture, schema=schema)
