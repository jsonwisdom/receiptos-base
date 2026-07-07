#!/usr/bin/env python3
import json
import sys
from pathlib import Path

RECEIPT_PATH = Path("receipts/ext-063-local-compile-validation-gate.json")

EXPECTED = {
    "issue": "EXT-063",
    "title": "Local Compile Validation Gate",
    "status": "LOCAL_COMPILE_VALIDATION_LOCKED",
    "depends_on": ["EXT-061", "EXT-062"],
    "target_contract": "contracts/mock/EXT060MockWitnessBadge.sol",
    "policy_guard": "verify_ext_061_solidity_static_policy_guard.py",
    "validation_mode": "local_compile_check_only",
    "compile_validation_allowed": True,
    "compile_allowed": False,
    "chain_publish_allowed": False,
    "artifact_publish_allowed": False,
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

REQUIRED_PRECONDITIONS = {
    "static_policy_guard_passes",
    "mock_contract_exists",
    "constructor_reverts_public_use_semantics",
    "transfer_functions_revert",
    "receipt_hash_required",
    "duplicate_receipt_guard_present",
    "zero_power_constants_present",
}

FORBIDDEN_RESULTS = {
    "chain_publish",
    "public_contract_address",
    "published_binary_artifact",
    "authority_grant",
    "vote_power_assignment",
    "truth_claim_promotion",
}

SOURCE_REQUIRED = [
    "pragma solidity ^0.8.20;",
    "contract EXT060MockWitnessBadge",
    "DEPLOY_ALLOWED = false",
    "AUTHORITY = false",
    "TRUTH_CLAIM = false",
    "BADGE_POWER = 0",
    "VOTE_POWER = 0",
    "revert MockOnlyNoDeployAuthority();",
    "revert TransferDisabled();",
    "receiptHash == bytes32(0)",
    "receiptMinted[receiptHash]",
]

SOURCE_FORBIDDEN = [
    "DEPLOY_ALLOWED = true",
    "AUTHORITY = true",
    "TRUTH_CLAIM = true",
    "BADGE_POWER = 1",
    "VOTE_POWER = 1",
    "function delegateVotePower",
    "function settleOutcome",
    "function claimTruth",
]


def fail(message: str) -> None:
    print(f"EXT-063 FAIL: {message}")
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

    preconditions = set(receipt.get("required_preconditions", []))
    forbidden_results = set(receipt.get("forbidden_results", []))

    require(preconditions == REQUIRED_PRECONDITIONS, f"required_preconditions mismatch: {preconditions!r}")
    require(forbidden_results == FORBIDDEN_RESULTS, f"forbidden_results mismatch: {forbidden_results!r}")

    target_contract = Path(receipt["target_contract"])
    policy_guard = Path(receipt["policy_guard"])

    require(target_contract.exists(), f"missing target contract: {target_contract}")
    require(policy_guard.exists(), f"missing policy guard: {policy_guard}")

    source = target_contract.read_text()
    guard_source = policy_guard.read_text()

    for marker in SOURCE_REQUIRED:
        require(marker in source, f"missing source marker: {marker}")

    for marker in SOURCE_FORBIDDEN:
        require(marker not in source, f"forbidden source marker present: {marker}")

    require("EXT-061 PASS" in guard_source, "policy guard must expose EXT-061 PASS path")
    require("compile_allowed" in guard_source, "policy guard must check compile_allowed")
    require("deploy_allowed" in guard_source, "policy guard must check deploy_allowed")

    require(source.count("revert TransferDisabled();") >= 2, "both transfer functions must revert")
    require("constructor()" in source and "revert MockOnlyNoDeployAuthority();" in source, "constructor must reject public-use semantics")

    require(receipt.get("compile_validation_allowed") is True, "local compile validation may be allowed")
    require(receipt.get("compile_allowed") is False, "compile_allowed must remain false")
    require(receipt.get("chain_publish_allowed") is False, "chain_publish_allowed must remain false")
    require(receipt.get("artifact_publish_allowed") is False, "artifact_publish_allowed must remain false")
    require(receipt.get("authority") is False and receipt.get("truth_claim") is False, "authority and truth_claim must remain false")
    require(receipt.get("badge_power") == 0 and receipt.get("vote_power") == 0, "badge_power and vote_power must remain zero")
    require(receipt.get("governance_action_allowed") is False, "governance_action_allowed must remain false")
    require(receipt.get("promotion_allowed") is False, "promotion_allowed must remain false")

    print("EXT-063 PASS: local compile validation gate ready; policy guard satisfied; compile/public-chain publishing disabled; authority=false; truth_claim=false; vote_power=0")


if __name__ == "__main__":
    main()
