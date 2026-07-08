import pytest

from receiptos.core.authority import AuthorityViolation, enforce_authority


def test_runtime_gate_accepts_literal_false():
    assert enforce_authority(False) is True


def test_runtime_gate_rejects_non_false_values():
    for candidate in [not False, None, 0, "false"]:
        with pytest.raises(AuthorityViolation):
            enforce_authority(candidate)
