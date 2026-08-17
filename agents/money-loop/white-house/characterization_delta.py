from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

ComparisonState = Literal["MATCH", "DELTA_OBSERVED"]
ResponseState = Literal["NOT_YET_RECEIVED", "PASS", "CONFLICT", "GAP"]


@dataclass(frozen=True)
class CharacterizationDeltaAudit:
    audit_type: str
    publisher: str
    underlying_record_owner: str
    observed_characterization: str
    underlying_record_characterization: str
    comparison_state: ComparisonState
    question_recipient: str
    question: str
    response_state: ResponseState
    claim_true: str = "NOT_ASSERTED"
    which_characterization_is_correct: str = "NOT_ASSERTED"
    intent: str = "NOT_ASSERTED"
    deception: str = "NOT_ASSERTED"
    guilt: str = "NOT_ASSERTED"
    authority_created: bool = False

    def validate(self) -> None:
        if self.audit_type != "CHARACTERIZATION_DELTA":
            raise ValueError("wrong audit type")
        if self.publisher != "WHITE_HOUSE":
            raise ValueError("publisher must remain WHITE_HOUSE for this lane")
        if self.underlying_record_owner != "DOJ":
            raise ValueError("record owner must remain DOJ for this lane")
        expected = (
            "MATCH"
            if self.observed_characterization == self.underlying_record_characterization
            else "DELTA_OBSERVED"
        )
        if self.comparison_state != expected:
            raise ValueError("comparison state mismatch")
        if self.question_recipient != "DOJ":
            raise ValueError("neutral source-owner question must route to DOJ")
        if self.claim_true != "NOT_ASSERTED":
            raise ValueError("claim truth cannot be promoted by comparison")
        if self.which_characterization_is_correct != "NOT_ASSERTED":
            raise ValueError("correctness cannot be promoted by comparison")
        for field_name in ("intent", "deception", "guilt"):
            if getattr(self, field_name) != "NOT_ASSERTED":
                raise ValueError(f"{field_name} cannot be inferred from a characterization delta")
        if self.authority_created:
            raise ValueError("authority_created must remain false")

    def to_dict(self) -> dict[str, object]:
        self.validate()
        return asdict(self)


def build_audit(observed_characterization: str, underlying_record_characterization: str) -> CharacterizationDeltaAudit:
    state: ComparisonState = (
        "MATCH"
        if observed_characterization == underlying_record_characterization
        else "DELTA_OBSERVED"
    )
    return CharacterizationDeltaAudit(
        audit_type="CHARACTERIZATION_DELTA",
        publisher="WHITE_HOUSE",
        underlying_record_owner="DOJ",
        observed_characterization=observed_characterization,
        underlying_record_characterization=underlying_record_characterization,
        comparison_state=state,
        question_recipient="DOJ",
        question="Does DOJ consider the White House characterization an accurate representation of DOJ's underlying record?",
        response_state="NOT_YET_RECEIVED",
        authority_created=False,
    )


def classify_response(*, answer_received: bool, agrees: bool | None) -> ResponseState:
    if not answer_received:
        return "GAP"
    if agrees is True:
        return "PASS"
    if agrees is False:
        return "CONFLICT"
    return "GAP"
