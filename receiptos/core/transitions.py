from receiptos.core.authority import enforce_authority


class TransitionViolation(ValueError):
    """Raised when a ReceiptOS state transition is not allowed."""


ALLOWED_TRANSITIONS = {
    "OBSERVED": {"CAPTURED", "REJECTED", "DISPUTED"},
    "CAPTURED": {"CLASSIFIED", "REJECTED", "DISPUTED"},
    "CLASSIFIED": {"PACKAGED", "REJECTED", "DISPUTED"},
    "PACKAGED": {"HASHED", "REJECTED", "DISPUTED"},
    "HASHED": {"PINNED", "REJECTED", "DISPUTED"},
    "PINNED": {"ATTESTED", "REJECTED", "DISPUTED"},
    "ATTESTED": {"APPROVED", "REJECTED", "DISPUTED"},
    "APPROVED": {"VARIANT_GENERATED", "REJECTED", "DISPUTED"},
    "VARIANT_GENERATED": {"PUBLISHED", "REJECTED", "DISPUTED"},
    "PUBLISHED": {"REPLAYED", "DISPUTED"},
    "REPLAYED": {"ARCHIVED", "DISPUTED"},
    "REJECTED": {"ARCHIVED"},
    "DISPUTED": {"EVIDENCE_REVIEW"},
    "EVIDENCE_REVIEW": {"REJECTED", "APPROVED", "ARCHIVED"},
    "ARCHIVED": set(),
}


TERMINAL_STATES = {"ARCHIVED"}


def assert_transition_allowed(from_state, to_state, *, authority=False):
    """Validate a ReceiptOS transition without mutating receipt state."""
    enforce_authority(authority)

    if from_state not in ALLOWED_TRANSITIONS:
        raise TransitionViolation(f"unknown from_state: {from_state!r}")

    if to_state not in ALLOWED_TRANSITIONS:
        raise TransitionViolation(f"unknown to_state: {to_state!r}")

    if from_state in TERMINAL_STATES:
        raise TransitionViolation(f"terminal state cannot transition: {from_state!r}")

    allowed = ALLOWED_TRANSITIONS[from_state]
    if to_state not in allowed:
        raise TransitionViolation(f"forbidden transition: {from_state!r} -> {to_state!r}")

    return True
