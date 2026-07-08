import copy
import json
from pathlib import Path

from receiptos.core.hash import canonical_receipt_hash


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "card_001_seed.json"
EXPECTED_CARD_001_HASH = "sha256:2e37f5dffe884c2223381fa1cddbbd01d42c9f3cf91c5492931e14c5b33474af"


def load_fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_card_001_fixture_has_expected_non_zero_canonical_hash():
    card = load_fixture()

    assert card["receipt_id"] == EXPECTED_CARD_001_HASH
    assert card["core_hash"] == EXPECTED_CARD_001_HASH
    assert card["custody"]["chain_head"] == EXPECTED_CARD_001_HASH
    assert card["birth_witness"]["witness_hash"] == EXPECTED_CARD_001_HASH.removeprefix("sha256:")
    assert canonical_receipt_hash(card) == EXPECTED_CARD_001_HASH


def test_mutable_publication_metadata_does_not_change_canonical_hash():
    card = load_fixture()
    mutated = copy.deepcopy(card)

    mutated["created_at"] = "2099-01-01T00:00:00Z"
    mutated["updated_at"] = "2099-01-01T00:00:00Z"
    mutated["approval_status"] = "approved"
    mutated["publish_targets"] = ["zora", "x"]
    mutated["variants"] = {"x_post": {"text": "mutable presentation"}}
    mutated["replay_status"] = {"count": 99, "last_replay": "2099-01-01T00:00:00Z"}

    assert canonical_receipt_hash(mutated) == EXPECTED_CARD_001_HASH
