#!/usr/bin/env python3
import json
import sys
from pathlib import Path

RECEIPT_PATH = Path("receipts/ext-051-governance-membrane.json")

EXPECTED = {
    "issue": "EXT-051",
    "title": "Governance Membrane: No Vote From Witness",
    "status": "GOVERNANCE_MEMBRANE_LOCKED",
    "depends_on": ["EXT-048", "EXT-049", "EXT-050"],
    "authority": False,
    "truth_claim": False,
    "resolution_semantics": "absent",
    "runtime_mode": "witness_only",
    "governance_action_allowed": False,
    "vote_power": 0,
    "recommendation_allowed": True,
    "promotion_allowed": False,
}

EXPECTED_MEMBRANE = {
    "witness_receipts_may_inform_review": True,
    "witness_receipts_may_cast_vote": False,
    "witness_receipts_may_claim_authority": False,
    "witness_receipts_may_promote_truth": False,
}


def fail(message: str) -> None:
    print(f"EXT-051 FAIL: {message}")
    sys.exit(1)


def main() -> None:
    if not RECEIPT_PATH.exists():
        fail(f"missing receipt: {RECEIPT_PATH}")

    try:
        receipt = json.loads(RECEIPT_PATH.read_text())
    except json.JSONDecodeError as exc:
        fail(f"invalid json: {exc}")

    for key, expected_value in EXPECTED.items():
        actual_value = receipt.get(key)
        if actual_value != expected_value:
            fail(f"{key}: expected {expected_value!r}, got {actual_value!r}")

    membrane = receipt.get("membrane")
    if not isinstance(membrane, dict):
        fail("membrane must be an object")

    for key, expected_value in EXPECTED_MEMBRANE.items():
        actual_value = membrane.get(key)
        if actual_value != expected_value:
            fail(f"membrane.{key}: expected {expected_value!r}, got {actual_value!r}")

    if receipt.get("authority") is not False:
        fail("authority must be false")

    if receipt.get("truth_claim") is not False:
        fail("truth_claim must be false")

    if receipt.get("resolution_semantics") != "absent":
        fail("resolution_semantics must be absent")

    if receipt.get("runtime_mode") != "witness_only":
        fail("runtime_mode must be witness_only")

    if receipt.get("governance_action_allowed") is not False:
        fail("governance actions must not be allowed from witness receipts")

    if receipt.get("vote_power") != 0:
        fail("vote_power must be zero")

    if receipt.get("recommendation_allowed") is not True:
        fail("recommendation must remain allowed")

    if receipt.get("promotion_allowed") is not False:
        fail("promotion must not be allowed")

    print("EXT-051 PASS: witness receipts may inform review; no vote, no authority, no truth promotion")


if __name__ == "__main__":
    main()
