from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

SEMANTIC_TYPE = "BOUNDED_EVIDENCE_GATE_DISPOSITION"

ALLOWED_PROVEN_RENDERINGS = {
    "Evidence gate disposition: PROVEN",
    "Observer result: PROVEN",
    "Required evidence conditions were satisfied",
}

FORBIDDEN_PROMOTIONS = {
    "CLAIM_PROVEN",
    "ALLEGATION_PROVEN",
    "FRAUD_PROVEN",
    "GUILT_ESTABLISHED",
    "DOJ_ENDORSEMENT",
    "LEGAL_FINDING",
}

FORBIDDEN_RENDERINGS = {
    "Claim proven",
    "Fraud proven",
    "Allegation proven",
    "DOJ confirmed",
    "DOJ endorsed",
    "Guilt established",
    "Legal finding",
    "Misconduct established",
}


@dataclass(frozen=True)
class SemanticRenderResult:
    observer_result: str
    semantic_type: str
    rendered_text: str
    evidence_gate_proven: bool
    claim_proven: bool
    allegation_proven: bool
    fraud_proven: bool
    guilt_established: bool
    doj_endorsement: bool
    legal_finding: bool
    fail_closed: bool
    authority_created: bool = False

    def validate(self) -> None:
        if self.semantic_type != SEMANTIC_TYPE:
            raise ValueError("semantic type widening is forbidden")
        if self.authority_created:
            raise ValueError("authority_created must remain false")
        if self.observer_result == "PROVEN":
            if not self.evidence_gate_proven:
                raise ValueError("PROVEN must preserve evidence-gate meaning")
            if any((
                self.claim_proven,
                self.allegation_proven,
                self.fraud_proven,
                self.guilt_established,
                self.doj_endorsement,
                self.legal_finding,
            )):
                raise ValueError("PROVEN cannot widen into claim/legal/misconduct semantics")
            if self.rendered_text not in ALLOWED_PROVEN_RENDERINGS:
                raise ValueError("unapproved PROVEN rendering")
        if self.rendered_text in FORBIDDEN_RENDERINGS:
            raise ValueError("forbidden semantic promotion in rendering")


def render_observer_result(observer_result: str, *, wording: str = "Observer result: PROVEN") -> SemanticRenderResult:
    if observer_result != "PROVEN":
        return SemanticRenderResult(
            observer_result=observer_result,
            semantic_type=SEMANTIC_TYPE,
            rendered_text=f"Observer result: {observer_result}",
            evidence_gate_proven=False,
            claim_proven=False,
            allegation_proven=False,
            fraud_proven=False,
            guilt_established=False,
            doj_endorsement=False,
            legal_finding=False,
            fail_closed=True,
            authority_created=False,
        )

    result = SemanticRenderResult(
        observer_result="PROVEN",
        semantic_type=SEMANTIC_TYPE,
        rendered_text=wording,
        evidence_gate_proven=True,
        claim_proven=False,
        allegation_proven=False,
        fraud_proven=False,
        guilt_established=False,
        doj_endorsement=False,
        legal_finding=False,
        fail_closed=True,
        authority_created=False,
    )
    result.validate()
    return result


def assert_no_forbidden_promotions(promotions: Iterable[str]) -> None:
    overlap = FORBIDDEN_PROMOTIONS.intersection(promotions)
    if overlap:
        raise ValueError(f"forbidden semantic promotions: {sorted(overlap)}")
