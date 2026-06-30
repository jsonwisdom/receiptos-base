#!/usr/bin/env python3
import json
import sys
from pathlib import Path

RECEIPT_PATH = Path("receipts/ext-056-badge-minting-membrane.json")

EXPECTED = {
    "issue": "EXT-056",
    "title": "Badge Minting Membrane",
    "status": "BADGE_MINTING_MEMBRANE_LOCKED",
    "depends_on": ["EXT-054", "EXT-055"],
    "runtime_mode": "witness_only",
    "authority": False,
    "truth_claim": False,
    "resolution_semantics": "absent",
    "badge_minting_allowed": True,
    "badge_power": 0,
    "vote_power": 0,
    "governance_action_allowed": False,
    "transfer_governance_rights": False,
    "promotion_allowed": False,
}

ALLOWED_BADGE_ACTIONS = {"Inspect", "Replay", "Verify", "Challenge", "Trace"}
FORBIDDEN_BADGE_ACTIONS = {
    "Vote",
    "Resolve",
    "Promote Truth",
    "Grant Authority",
    "Execute Governance",
    "Settle Outcome",
}
FORBIDDEN_MINT_REPRESENTATIONS = {
    "truth",
    "authority",
    "governance power",
    "market resolution",
    "vote delegation",
}


def fail(message: str) -> None:
    print(f"EXT-056 FAIL: {message}")
    sys.exit(1)


def expect_equal(receipt: dict, key: str, expected_value) -> None:
    actual_value = receipt.get(key)
    if actual_value != expected_value:
        fail(f"{key}: expected {expected_value!r}, got {actual_value!r}")


def main() -> None:
    if not RECEIPT_PATH.exists():
        fail(f"missing receipt: {RECEIPT_PATH}")

    try:
        receipt = json.loads(RECEIPT_PATH.read_text())
    except json.JSONDecodeError as exc:
        fail(f"invalid json: {exc}")

    for key, expected_value in EXPECTED.items():
        expect_equal(receipt, key, expected_value)

    semantics = receipt.get("mint_semantics")
    if not isinstance(semantics, dict):
        fail("mint_semantics must be an object")

    if semantics.get("standard_model") != "ERC-1155-style completion badge":
        fail("standard_model must remain ERC-1155-style completion badge")

    if semantics.get("mint_represents") != "witness action completion":
        fail("mint must represent witness action completion only")

    actual_not_represent = set(semantics.get("mint_does_not_represent", []))
    if actual_not_represent != FORBIDDEN_MINT_REPRESENTATIONS:
        fail("mint_does_not_represent must block truth, authority, governance power, market resolution, and vote delegation")

    actual_allowed = set(semantics.get("allowed_badge_actions", []))
    if actual_allowed != ALLOWED_BADGE_ACTIONS:
        fail(f"allowed_badge_actions mismatch: {actual_allowed!r}")

    actual_forbidden = set(semantics.get("forbidden_badge_actions", []))
    if actual_forbidden != FORBIDDEN_BADGE_ACTIONS:
        fail(f"forbidden_badge_actions mismatch: {actual_forbidden!r}")

    if actual_allowed & actual_forbidden:
        fail("badge action cannot be both allowed and forbidden")

    if receipt.get("badge_power") != 0:
        fail("badge_power must be zero")

    if receipt.get("vote_power") != 0:
        fail("vote_power must be zero")

    if receipt.get("authority") is not False:
        fail("authority must be false")

    if receipt.get("truth_claim") is not False:
        fail("truth_claim must be false")

    if receipt.get("governance_action_allowed") is not False:
        fail("badge minting must not allow governance action")

    if receipt.get("transfer_governance_rights") is not False:
        fail("badges must not transfer governance rights")

    if receipt.get("promotion_allowed") is not False:
        fail("badge minting must not allow truth promotion")

    print("EXT-056 PASS: badge minting intent allowed; no vote, no authority, no truth promotion, no governance rights")


if __name__ == "__main__":
    main()
