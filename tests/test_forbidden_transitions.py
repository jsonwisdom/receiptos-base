import pytest

from receiptos.core.authority import AuthorityViolation
from receiptos.core.transitions import TransitionViolation, assert_transition_allowed


def test_canonical_transition_path_is_allowed():
    path = [
        "OBSERVED",
        "CAPTURED",
        "CLASSIFIED",
        "PACKAGED",
        "HASHED",
        "PINNED",
        "ATTESTED",
        "APPROVED",
        "VARIANT_GENERATED",
        "PUBLISHED",
        "REPLAYED",
        "ARCHIVED",
    ]

    for from_state, to_state in zip(path, path[1:]):
        assert assert_transition_allowed(from_state, to_state, authority=False) is True


@pytest.mark.parametrize(
    ("from_state", "to_state"),
    [
        ("CAPTURED", "APPROVED"),
        ("ATTESTED", "VARIANT_GENERATED"),
        ("PUBLISHED", "VARIANT_GENERATED"),
        ("PUBLISHED", "ARCHIVED"),
        ("ARCHIVED", "OBSERVED"),
        ("REJECTED", "APPROVED"),
    ],
)
def test_forbidden_transitions_are_rejected(from_state, to_state):
    with pytest.raises(TransitionViolation):
        assert_transition_allowed(from_state, to_state, authority=False)


def test_transition_runner_rejects_authority_change_attempt():
    with pytest.raises(AuthorityViolation):
        assert_transition_allowed("OBSERVED", "CAPTURED", authority=True)
