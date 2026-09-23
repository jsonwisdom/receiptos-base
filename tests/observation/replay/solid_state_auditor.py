#!/usr/bin/env python3
"""Deterministic, non-authoritative JSON audit pipeline.

The rubric is the subject. Evidence absence is never promoted to non-existence.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


class EvidenceStatus(str, Enum):
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    CONFLICTING = "CONFLICTING"
    INDETERMINATE = "INDETERMINATE"


class ReplayStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_REPRODUCIBLE = "NOT_REPRODUCIBLE"
    NOT_RUN = "NOT_RUN"


class ReverseReplayStatus(str, Enum):
    VERIFIED = "VERIFIED"
    MISMATCH = "MISMATCH"
    ATTEMPTED = "ATTEMPTED"
    NOT_RUN = "NOT_RUN"


@dataclass(frozen=True)
class EvidenceItem:
    source: str
    content: Any
    sha256: str
    verified: bool = False
    observed_at: Optional[str] = None


@dataclass(frozen=True)
class AuditReceipt:
    claim: str
    observed_at: str
    evidence_status: EvidenceStatus
    replay_status: ReplayStatus
    reverse_replay_status: ReverseReplayStatus
    conflicts: int
    missing_receipts: int
    unverified_receipts: int
    authority_created: bool = False
    operator_required: bool = True
    reflection_notes: Tuple[str, ...] = field(default_factory=tuple)
    rubric_results: Tuple[Tuple[str, bool], ...] = field(default_factory=tuple)
    replay_input: Optional[dict] = None
    replay_output: Optional[dict] = None
    reverse_replay_output: Optional[dict] = None
    receipt_sha256: str = ""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_hex(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def make_evidence_item(
    source: str,
    content: Any,
    *,
    verified: bool = False,
    observed_at: Optional[str] = None,
) -> EvidenceItem:
    return EvidenceItem(
        source=source,
        content=content,
        sha256=sha256_hex(content),
        verified=verified,
        observed_at=observed_at,
    )


class SolidStateAuditor:
    """QUESTION -> EVIDENCE -> STATE -> RUBRIC -> REPLAY -> REFLECTION."""

    def __init__(self, rubric: Mapping[str, Callable[[dict], bool]]):
        self._rubric = dict(rubric)
        self._evidence: List[EvidenceItem] = []

    def submit_evidence(
        self,
        source: str,
        content: Any,
        *,
        verified: bool = False,
        observed_at: Optional[str] = None,
    ) -> EvidenceItem:
        item = make_evidence_item(
            source,
            content,
            verified=verified,
            observed_at=observed_at,
        )
        self._evidence.append(item)
        return item

    def audit(
        self,
        *,
        claim: str,
        observed_at: str,
        replay_fn: Callable[[dict], dict],
        reverse_replay_fn: Callable[[dict, dict], dict],
        conflict_fn: Optional[Callable[[Sequence[EvidenceItem]], Iterable[str]]] = None,
    ) -> AuditReceipt:
        state = self._build_state(observed_at)
        conflicts = tuple(conflict_fn(tuple(self._evidence))) if conflict_fn else tuple()
        evidence_status = self._assess_evidence(conflicts)

        try:
            replay_output = replay_fn(state)
            replay_status = ReplayStatus.PASS
        except Exception as exc:
            replay_output = {"error_type": type(exc).__name__, "error": str(exc)}
            replay_status = ReplayStatus.FAIL

        reverse_output: dict
        reverse_status: ReverseReplayStatus
        if replay_status is ReplayStatus.PASS:
            try:
                reverse_output = reverse_replay_fn(state, replay_output)
                reconstructed = reverse_output.get("reconstructed_input")
                if reconstructed is None:
                    reverse_status = ReverseReplayStatus.ATTEMPTED
                elif canonical_bytes(reconstructed) == canonical_bytes(state):
                    reverse_status = ReverseReplayStatus.VERIFIED
                else:
                    reverse_status = ReverseReplayStatus.MISMATCH
            except Exception as exc:
                reverse_output = {"error_type": type(exc).__name__, "error": str(exc)}
                reverse_status = ReverseReplayStatus.MISMATCH
        else:
            reverse_output = {"status": "skipped_due_to_failed_replay"}
            reverse_status = ReverseReplayStatus.NOT_RUN

        rubric_results = tuple(
            (name, bool(check(state))) for name, check in sorted(self._rubric.items())
        )
        rubric_failures = [name for name, passed in rubric_results if not passed]

        notes: List[str] = []
        if evidence_status is not EvidenceStatus.FULL:
            notes.append(f"Evidence state: {evidence_status.value}")
        if rubric_failures:
            notes.append(f"Rubric failures: {rubric_failures}")
        if replay_status is not ReplayStatus.PASS:
            notes.append("Replay failed; process is not presently reproducible.")
        if reverse_status is ReverseReplayStatus.MISMATCH:
            notes.append("Reverse replay did not reconstruct the canonical input state.")
        notes.append(
            "NEXT_BEST_AUDIT_QUESTION: "
            + self._next_question(evidence_status, rubric_failures, reverse_status)
        )

        body = {
            "claim": claim,
            "observed_at": observed_at,
            "evidence_status": evidence_status.value,
            "replay_status": replay_status.value,
            "reverse_replay_status": reverse_status.value,
            "conflicts": len(conflicts),
            "missing_receipts": sum(item.content is None for item in self._evidence),
            "unverified_receipts": sum(not item.verified for item in self._evidence),
            "authority_created": False,
            "operator_required": True,
            "reflection_notes": notes,
            "rubric_results": list(rubric_results),
            "replay_input": state,
            "replay_output": replay_output,
            "reverse_replay_output": reverse_output,
        }
        return AuditReceipt(
            claim=claim,
            observed_at=observed_at,
            evidence_status=evidence_status,
            replay_status=replay_status,
            reverse_replay_status=reverse_status,
            conflicts=len(conflicts),
            missing_receipts=body["missing_receipts"],
            unverified_receipts=body["unverified_receipts"],
            authority_created=False,
            operator_required=True,
            reflection_notes=tuple(notes),
            rubric_results=rubric_results,
            replay_input=state,
            replay_output=replay_output,
            reverse_replay_output=reverse_output,
            receipt_sha256=sha256_hex(body),
        )

    def _build_state(self, observed_at: str) -> dict:
        return {
            "observed_at": observed_at,
            "evidence_items": [asdict(item) for item in self._evidence],
            "evidence_count": len(self._evidence),
            "rubric_checks": sorted(self._rubric),
        }

    def _assess_evidence(self, conflicts: Sequence[str]) -> EvidenceStatus:
        if conflicts:
            return EvidenceStatus.CONFLICTING
        if not self._evidence:
            return EvidenceStatus.MISSING
        verified = sum(item.verified for item in self._evidence)
        missing = sum(item.content is None for item in self._evidence)
        if missing:
            return EvidenceStatus.PARTIAL if verified else EvidenceStatus.MISSING
        if verified == len(self._evidence):
            return EvidenceStatus.FULL
        return EvidenceStatus.PARTIAL if verified else EvidenceStatus.MISSING

    @staticmethod
    def _next_question(
        evidence_status: EvidenceStatus,
        rubric_failures: Sequence[str],
        reverse_status: ReverseReplayStatus,
    ) -> str:
        if evidence_status is not EvidenceStatus.FULL:
            return "Which exact receipt or source would resolve the current evidence state?"
        if rubric_failures:
            return f"What evidence or rule change would cause {list(rubric_failures)} to pass?"
        if reverse_status is not ReverseReplayStatus.VERIFIED:
            return "Which transformation prevents exact reconstruction of the canonical input?"
        return "What independent claim should be tested under this same rubric?"
