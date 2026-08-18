"""Lock Evidence Graph (LEG) traversal and structural checks.

Implements the graph model defined in the M7 Lock Evidence Graph contract:
- Node types: AuthorizationReceipt, EvidenceReceipt, DecisionReceipt, LockReceipt
- Edge types: supports, authorizes, locks, derives_from, supersedes
- Structural invariants: acyclicity, required edges, forbidden edges
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class Node:
    id: str
    type: str
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    from_id: str
    to_id: str
    type: str


class LEGGraph:
    """In-memory representation of a Lock Evidence Graph."""

    ALLOWED_NODE_TYPES = {
        "AuthorizationReceipt",
        "EvidenceReceipt",
        "DecisionReceipt",
        "LockReceipt",
    }

    ALLOWED_EDGE_TYPES = {
        "supports",
        "authorizes",
        "locks",
        "derives_from",
        "supersedes",
        "supported_by",  # inverse convenience edge used in fixtures
    }

    def __init__(self) -> None:
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []

    def add_node(self, node_id: str, node_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
        if node_type not in self.ALLOWED_NODE_TYPES:
            raise ValueError(f"Unknown node type: {node_type}")
        self.nodes[node_id] = Node(id=node_id, type=node_type, payload=payload or {})

    def add_edge(self, from_id: str, to_id: str, edge_type: str) -> None:
        if edge_type not in self.ALLOWED_EDGE_TYPES:
            raise ValueError(f"Unknown edge type: {edge_type}")
        if from_id not in self.nodes or to_id not in self.nodes:
            raise ValueError(f"Edge references unknown node: {from_id} -> {to_id}")
        self.edges.append(Edge(from_id=from_id, to_id=to_id, type=edge_type))

    def load_from_dict(self, data: Dict[str, Any]) -> None:
        """Load nodes and edges from a fixture-style dict."""
        for n in data.get("nodes", []):
            self.add_node(n["id"], n["type"], n.get("payload"))
        for e in data.get("edges", []):
            self.add_edge(e["from"], e["to"], e["type"])

    def is_acyclic(self) -> bool:
        """Kahn's algorithm / DFS cycle detection."""
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        for e in self.edges:
            adj[e.from_id].append(e.to_id)

        WHITE, GRAY, BLACK = 0, 1, 2
        color = {nid: WHITE for nid in self.nodes}

        def dfs(u: str) -> bool:
            color[u] = GRAY
            for v in adj[u]:
                if color[v] == GRAY:
                    return False  # back edge → cycle
                if color[v] == WHITE and not dfs(v):
                    return False
            color[u] = BLACK
            return True

        for nid in self.nodes:
            if color[nid] == WHITE:
                if not dfs(nid):
                    return False
        return True

    def outgoing(self, node_id: str, edge_type: Optional[str] = None) -> List[Edge]:
        return [
            e for e in self.edges
            if e.from_id == node_id and (edge_type is None or e.type == edge_type)
        ]

    def incoming(self, node_id: str, edge_type: Optional[str] = None) -> List[Edge]:
        return [
            e for e in self.edges
            if e.to_id == node_id and (edge_type is None or e.type == edge_type)
        ]
