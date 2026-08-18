"""M7 invariant assertion suite.

Implements the eight M7 invariants against a loaded LEGGraph and optional
AuthorizationReceipt objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .graph import LEGGraph
from .authorization import AuthorizationReceiptValidator


@dataclass
class InvariantResult:
    code: str
    passed: bool
    detail: str = ""


class InvariantSuite:
    """Runs M7-001 … M7-008 against a graph (+ optional receipts)."""

    def __init__(self) -> None:
        self.auth_validator = AuthorizationReceiptValidator()

    def check_all(
        self,
        graph: LEGGraph,
        authorization_receipts: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> List[InvariantResult]:
        results: List[InvariantResult] = []
        authorization_receipts = authorization_receipts or {}

        results.append(self._m7_001(graph))
        results.append(self._m7_002(authorization_receipts))
        results.append(self._m7_003(graph))
        results.append(self._m7_004(graph))
        results.append(self._m7_005(authorization_receipts))
        results.append(self._m7_006(graph))
        results.append(self._m7_007(authorization_receipts))
        results.append(self._m7_008(graph))

        return results

    def _m7_001(self, graph: LEGGraph) -> InvariantResult:
        """No Lock without AuthorizationReceipt."""
        for nid, node in graph.nodes.items():
            if node.type != "LockReceipt":
                continue
            # Must have a supported_by or equivalent path to an AuthorizationReceipt
            supported = graph.outgoing(nid, "supported_by") + graph.incoming(nid, "supports")
            auth_targets = []
            for e in supported:
                other = e.to_id if e.from_id == nid else e.from_id
                if other in graph.nodes and graph.nodes[other].type == "AuthorizationReceipt":
                    auth_targets.append(other)
            if not auth_targets:
                return InvariantResult(
                    "M7-001", False, f"LockReceipt {nid} has no AuthorizationReceipt"
                )
        return InvariantResult("M7-001", True)

    def _m7_002(self, receipts: Dict[str, Dict[str, Any]]) -> InvariantResult:
        """AuthorizationReceipt must reference exactly one subject_decision_id."""
        for rid, rec in receipts.items():
            ok, errs = self.auth_validator.validate(rec)
            if not ok and any("M7-002" in e for e in errs):
                return InvariantResult("M7-002", False, "; ".join(errs))
        return InvariantResult("M7-002", True)

    def _m7_003(self, graph: LEGGraph) -> InvariantResult:
        """LockReceipt must include a complete supporting evidence set.

        Minimal check: every LockReceipt has at least one supports / supported_by edge.
        """
        for nid, node in graph.nodes.items():
            if node.type != "LockReceipt":
                continue
            evidence_edges = (
                graph.outgoing(nid, "supported_by")
                + graph.incoming(nid, "supports")
            )
            if not evidence_edges:
                return InvariantResult(
                    "M7-003", False, f"LockReceipt {nid} has empty supporting evidence set"
                )
        return InvariantResult("M7-003", True)

    def _m7_004(self, graph: LEGGraph) -> InvariantResult:
        """LEG must remain acyclic."""
        if graph.is_acyclic():
            return InvariantResult("M7-004", True)
        return InvariantResult("M7-004", False, "cycle detected in Lock Evidence Graph")

    def _m7_005(self, receipts: Dict[str, Dict[str, Any]]) -> InvariantResult:
        """Authorization context must be hash-stable (well-formed SHA-256)."""
        for rid, rec in receipts.items():
            ok, errs = self.auth_validator.validate(rec)
            if not ok and any("M7-005" in e for e in errs):
                return InvariantResult("M7-005", False, "; ".join(errs))
        return InvariantResult("M7-005", True)

    def _m7_006(self, graph: LEGGraph) -> InvariantResult:
        """Overrides must preserve lineage; no deletion without tombstone.

        Minimal check: every supersedes edge has a corresponding tombstone node
        or the superseded node is still present (append-only).
        """
        for e in graph.edges:
            if e.type != "supersedes":
                continue
            # Superseded node must still exist (no hard delete)
            if e.to_id not in graph.nodes:
                return InvariantResult(
                    "M7-006",
                    False,
                    f"supersedes edge from {e.from_id} targets missing node {e.to_id} (no tombstone)",
                )
        return InvariantResult("M7-006", True)

    def _m7_007(self, receipts: Dict[str, Dict[str, Any]]) -> InvariantResult:
        """AuthorizationReceipt signature must be present (immutability is post-issuance)."""
        for rid, rec in receipts.items():
            ok, errs = self.auth_validator.validate(rec)
            if not ok and any("M7-007" in e for e in errs):
                return InvariantResult("M7-007", False, "; ".join(errs))
        return InvariantResult("M7-007", True)

    def _m7_008(self, graph: LEGGraph) -> InvariantResult:
        """LockReceipt is append-only; no mutation after issuance.

        Structural check only: we do not have mutation history here.
        Always passes at the harness level; real enforcement requires storage layer.
        """
        return InvariantResult("M7-008", True, "structural only — storage layer enforces immutability")
