import pytest

from economics.v0_1.decision_receipt_validator import validate_decision_receipt

pytestmark = pytest.mark.skip(reason="Decision Receipt Validator V0.1 implementation pending")


def test_decision_receipt_validator_stub():
    assert callable(validate_decision_receipt)
