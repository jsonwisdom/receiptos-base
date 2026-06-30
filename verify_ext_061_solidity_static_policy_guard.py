#!/usr/bin/env python3
import json
import sys
from pathlib import Path

RECEIPT_PATH = Path("receipts/ext-061-solidity-static-policy-guard.json")

EXPECTED = {
    "issue": "EXT-061",
    "title": "Solidity Static Policy Guard",
    "status": "STATIC_POLICY_GUARD_LOCKED",
    "depends_on": ["EXT-060"],
    "target_contract": "contracts/mock/EXT060MockWitnessBadge.sol",
    "guard_path": "verify_ext_061_solidity_static_policy_guard.py",
    "guard_mode": "static_source_scan",
    "compile_allowed": False,
    "deploy_allowed": False,
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

REQUIRED_FUNCTION_MARKERS = [
    "function mintCompletionBadge",
    "function hasReceiptBadge",
    "function receiptHashOf",
    "function badgeMetadata",
    "function safeTransferFrom",
    "function safeBatchTransferFrom",
    "function vote",
    "function resolve",
    "function grantAuthority",
    "function promoteTruth",
    "function executeGovernance",
]

REQUIRED_REVERTS = {
    "constructor_revert": "revert MockOnlyNoDeployAuthority();",
    "receipt_hash_revert": "revert ReceiptHashRequired();",
    "witness_completion_revert": "revert WitnessCompletionRequired();",
    "duplicate_receipt_revert": "revert DuplicateReceiptBadge();",
    "transfer_revert": "revert TransferDisabled();",
    "governance_revert": "revert GovernanceDisabled();",
    "truth_revert": "revert TruthPromotionDisabled();",
}


def fail(message: str) -> None:
    print(f"EXT-061 FAIL: {message}")
    sys.exit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    require(RECEIPT_PATH.exists(), f"missing receipt: {RECEIPT_PATH}")

    try:
        receipt = json.loads(RECEIPT_PATH.read_text())
    except json.JSONDecodeError as exc:
        fail(f"invalid json: {exc}")

    for key, expected_value in EXPECTED.items():
        actual_value = receipt.get(key)
        require(actual_value == expected_value, f"{key}: expected {expected_value!r}, got {actual_value!r}")

    target_contract = Path(receipt["target_contract"])
    require(target_contract.exists(), f"missing target contract: {target_contract}")

    source = target_contract.read_text()

    required_markers = receipt.get("required_markers")
    forbidden_markers = receipt.get("forbidden_markers")

    require(isinstance(required_markers, list) and required_markers, "required_markers must be a non-empty list")
    require(isinstance(forbidden_markers, list) and forbidden_markers, "forbidden_markers must be a non-empty list")

    for marker in required_markers:
        require(marker in source, f"missing required source marker: {marker}")

    for marker in forbidden_markers:
        require(marker not in source, f"forbidden source marker present: {marker}")

    for marker in REQUIRED_FUNCTION_MARKERS:
        require(marker in source, f"missing required function marker: {marker}")

    for name, marker in REQUIRED_REVERTS.items():
        require(marker in source, f"missing required revert {name}: {marker}")

    require(source.count("revert TransferDisabled();") >= 2, "both transfer functions must revert TransferDisabled")
    require("constructor()" in source and "revert MockOnlyNoDeployAuthority();" in source, "constructor must revert to prevent deploy semantics")
    require("receiptHash == bytes32(0)" in source, "receipt hash zero check required")
    require("receiptMinted[receiptHash]" in source, "duplicate receipt guard required")
    require("return true;" in source, "mock mint success path must be explicit")

    require(receipt.get("compile_allowed") is False, "compile_allowed must remain false")
    require(receipt.get("deploy_allowed") is False, "deploy_allowed must remain false")
    require(receipt.get("authority") is False, "authority must remain false")
    require(receipt.get("truth_claim") is False, "truth_claim must remain false")
    require(receipt.get("badge_power") == 0 and receipt.get("vote_power") == 0, "badge_power and vote_power must remain zero")
    require(receipt.get("governance_action_allowed") is False, "governance_action_allowed must remain false")
    require(receipt.get("promotion_allowed") is False, "promotion_allowed must remain false")

    print("EXT-061 PASS: Solidity static policy guard passed; compile/deploy disabled; authority, truth, vote, transfer, and governance paths blocked")


if __name__ == "__main__":
    main()
