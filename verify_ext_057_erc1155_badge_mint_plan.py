#!/usr/bin/env python3
import json
import sys
from pathlib import Path

RECEIPT_PATH = Path("receipts/ext-057-erc1155-badge-mint-plan.json")

EXPECTED = {
    "issue": "EXT-057",
    "title": "ERC-1155 Badge Mint Plan",
    "standard": "ERC-1155",
    "mint_represents": "witness_action_completion",
    "badge_power": 0,
    "vote_power": 0,
    "authority": False,
    "truth_claim": False,
    "governance_action_allowed": False,
    "transfer_governance_rights": False,
    "promotion_allowed": False,
}

EXPECTED_CONSTRAINTS = {
    "nonTransferable": True,
    "oneBadgePerReceipt": True,
    "receiptHashRequired": True,
    "badgeCannotVote": True,
    "badgeCannotResolve": True,
    "badgeCannotGrantAuthority": True,
}


def fail(message: str) -> None:
    print(f"EXT-057 FAIL: {message}")
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

    constraints = receipt.get("constraints")
    if not isinstance(constraints, dict):
        fail("constraints must be an object")

    for key, expected_value in EXPECTED_CONSTRAINTS.items():
        actual_value = constraints.get(key)
        if actual_value != expected_value:
            fail(f"constraints.{key}: expected {expected_value!r}, got {actual_value!r}")

    if receipt.get("standard") != "ERC-1155":
        fail("standard must be ERC-1155")

    if receipt.get("mint_represents") != "witness_action_completion":
        fail("mint must represent witness_action_completion only")

    if receipt.get("badge_power") != 0:
        fail("badge_power must be zero")

    if receipt.get("vote_power") != 0:
        fail("vote_power must be zero")

    if receipt.get("authority") is not False:
        fail("authority must be false")

    if receipt.get("truth_claim") is not False:
        fail("truth_claim must be false")

    if receipt.get("governance_action_allowed") is not False:
        fail("badge mint plan must not allow governance action")

    if receipt.get("transfer_governance_rights") is not False:
        fail("badge mint plan must not transfer governance rights")

    if receipt.get("promotion_allowed") is not False:
        fail("badge mint plan must not allow truth promotion")

    print("EXT-057 PASS: ERC-1155 badge mint plan constrained; completion evidence only; no vote, no authority, no truth promotion")


if __name__ == "__main__":
    main()
