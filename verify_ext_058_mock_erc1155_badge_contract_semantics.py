#!/usr/bin/env python3
import json
import sys
from pathlib import Path

RECEIPT_PATH = Path("receipts/ext-058-mock-erc1155-badge-contract-semantics.json")

EXPECTED = {
    "issue": "EXT-058",
    "title": "Mock ERC-1155 Badge Contract Semantics",
    "status": "MOCK_CONTRACT_SEMANTICS_LOCKED",
    "depends_on": ["EXT-056", "EXT-057"],
    "standard": "ERC-1155",
    "contract_mode": "mock_semantics_only",
    "deploy_allowed": False,
    "mint_represents": "witness_action_completion",
    "runtime_mode": "witness_only",
    "authority": False,
    "truth_claim": False,
    "resolution_semantics": "absent",
    "badge_power": 0,
    "vote_power": 0,
    "governance_action_allowed": False,
    "transfer_governance_rights": False,
    "promotion_allowed": False,
}

EXPECTED_SEMANTICS = {
    "nonTransferable": True,
    "oneBadgePerReceipt": True,
    "receiptHashRequired": True,
    "mintRequiresWitnessCompletion": True,
    "badgeCannotVote": True,
    "badgeCannotResolve": True,
    "badgeCannotGrantAuthority": True,
    "badgeCannotPromoteTruth": True,
    "badgeCannotExecuteGovernance": True,
    "transferFunctionReverts": True,
    "safeTransferFromReverts": True,
    "safeBatchTransferFromReverts": True,
}

ALLOWED_FUNCTIONS = {
    "mintCompletionBadge",
    "hasReceiptBadge",
    "receiptHashOf",
    "badgeMetadata",
}

FORBIDDEN_FUNCTIONS = {
    "vote",
    "resolve",
    "grantAuthority",
    "promoteTruth",
    "executeGovernance",
    "settleOutcome",
    "delegateVotePower",
}


def fail(message: str) -> None:
    print(f"EXT-058 FAIL: {message}")
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

    semantics = receipt.get("mock_contract_semantics")
    if not isinstance(semantics, dict):
        fail("mock_contract_semantics must be an object")

    for key, expected_value in EXPECTED_SEMANTICS.items():
        actual_value = semantics.get(key)
        if actual_value != expected_value:
            fail(f"mock_contract_semantics.{key}: expected {expected_value!r}, got {actual_value!r}")

    allowed = set(receipt.get("allowed_functions", []))
    forbidden = set(receipt.get("forbidden_functions", []))

    if allowed != ALLOWED_FUNCTIONS:
        fail(f"allowed_functions mismatch: {allowed!r}")

    if forbidden != FORBIDDEN_FUNCTIONS:
        fail(f"forbidden_functions mismatch: {forbidden!r}")

    if allowed & forbidden:
        fail("function cannot be both allowed and forbidden")

    if receipt.get("deploy_allowed") is not False:
        fail("mock semantics must not permit live deploy")

    if receipt.get("contract_mode") != "mock_semantics_only":
        fail("contract_mode must remain mock_semantics_only")

    if receipt.get("badge_power") != 0 or receipt.get("vote_power") != 0:
        fail("badge_power and vote_power must remain zero")

    if receipt.get("authority") is not False or receipt.get("truth_claim") is not False:
        fail("authority and truth_claim must remain false")

    if receipt.get("governance_action_allowed") is not False:
        fail("mock badge contract must not allow governance action")

    if receipt.get("transfer_governance_rights") is not False:
        fail("mock badge contract must not transfer governance rights")

    if receipt.get("promotion_allowed") is not False:
        fail("mock badge contract must not allow truth promotion")

    print("EXT-058 PASS: mock ERC-1155 badge semantics constrained; non-transferable, receipt-tied, zero power, no deploy authority")


if __name__ == "__main__":
    main()
