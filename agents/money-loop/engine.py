#!/usr/bin/env python3
"""Deterministic receipt-gated engine for Money Loop v0.1."""

from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Dict

STAGE_TRANSITIONS = {
    ("IDEA", "ASSET_CREATED"): "ASSET_CREATED",
    ("ASSET_CREATED", "PUBLISHED"): "PUBLISHED",
    ("PUBLISHED", "SETTLEMENT_SEEN"): "SETTLEMENT_SEEN",
    ("SETTLEMENT_SEEN", "REVENUE_VERIFIED"): "REVENUE_VERIFIED",
    ("REVENUE_VERIFIED", "PROFIT_VERIFIED"): "PROFIT_VERIFIED",
}

class GameError(ValueError):
    pass

def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")

def canonical_sha256(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(obj)).hexdigest()

def _require(condition: bool, message: str) -> None:
    if not condition:
        raise GameError(message)

def _require_evidence(event: Dict[str, Any], *, verified: bool) -> Dict[str, Any]:
    evidence = event.get("evidence")
    _require(isinstance(evidence, dict), "event.evidence must be an object")
    _require(isinstance(evidence.get("ref"), str) and evidence["ref"].strip(), "evidence.ref required")
    _require(isinstance(evidence.get("kind"), str) and evidence["kind"].strip(), "evidence.kind required")
    if verified:
        _require(evidence.get("verified") is True, "verified evidence required")
    return evidence

def _amount(event: Dict[str, Any]) -> int:
    value = event.get("amount_cents")
    _require(type(value) is int and value >= 0, "amount_cents must be a non-negative integer")
    return value

def apply_event(state: Dict[str, Any], event: Dict[str, Any]) -> Dict[str, Any]:
    _require(state.get("schema_version") == "MONEY_LOOP_GAME_V0_1", "unsupported state schema")
    _require(state.get("authority") is False, "authority must remain false")
    _require(event.get("authority", False) is False, "event cannot create authority")
    event_id = event.get("event_id")
    event_type = event.get("type")
    _require(isinstance(event_id, str) and event_id.strip(), "event_id required")
    _require(isinstance(event_type, str) and event_type.strip(), "event.type required")
    _require(all(r.get("event_id") != event_id for r in state.get("receipts", [])), "duplicate event_id")

    next_state = copy.deepcopy(state)
    before_hash = canonical_sha256(state)
    evidence = None

    if event_type == "COST_VERIFIED":
        evidence = _require_evidence(event, verified=True)
        amount = _amount(event)
        next_state["score"]["cost_verified_cents"] += amount
        next_state["flags"]["cost_verified"] = True
    elif event_type == "SETTLEMENT_SEEN":
        evidence = _require_evidence(event, verified=False)
        key = (state["stage"], event_type)
        _require(key in STAGE_TRANSITIONS, f"invalid transition {key}")
        next_state["stage"] = STAGE_TRANSITIONS[key]
    else:
        key = (state["stage"], event_type)
        _require(key in STAGE_TRANSITIONS, f"invalid transition {key}")
        evidence = _require_evidence(event, verified=True)

        if event_type == "ASSET_CREATED":
            next_state["score"]["assets_created"] += 1
        elif event_type == "PUBLISHED":
            next_state["score"]["published"] += 1
        elif event_type == "REVENUE_VERIFIED":
            amount = _amount(event)
            next_state["score"]["revenue_verified_cents"] += amount
            next_state["flags"]["revenue_verified"] = True
        elif event_type == "PROFIT_VERIFIED":
            _require(next_state["flags"]["revenue_verified"] is True, "revenue must be verified")
            _require(next_state["flags"]["cost_verified"] is True, "costs must be verified")
            revenue = next_state["score"]["revenue_verified_cents"]
            costs = next_state["score"]["cost_verified_cents"]
            next_state["score"]["profit_verified_cents"] = revenue - costs
            next_state["flags"]["profit_verified"] = True

        next_state["stage"] = STAGE_TRANSITIONS[key]

    next_state["round"] += 1
    next_state["receipts"].append({
        "event_id": event_id,
        "type": event_type,
        "evidence_ref": evidence["ref"],
        "evidence_kind": evidence["kind"],
        "evidence_verified": evidence.get("verified") is True,
        "authority": False,
    })
    _require(next_state["authority"] is False, "authority invariant violated")
    after_hash = canonical_sha256(next_state)
    return {
        "status": "PASS",
        "before_hash": before_hash,
        "after_hash": after_hash,
        "authority_created": False,
        "state": next_state,
    }

def load_json(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True)
    parser.add_argument("--event", required=True)
    parser.add_argument("--out")
    args = parser.parse_args()
    try:
        result = apply_event(load_json(args.state), load_json(args.event))
    except (OSError, json.JSONDecodeError, GameError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc), "authority_created": False}, sort_keys=True))
        return 1
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
