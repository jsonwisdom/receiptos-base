#!/usr/bin/env python3
import hashlib
import json
import sys
from pathlib import Path

RECEIPT_PATH = Path("receipts/ext-066-local-compile-unit-test-gate.json")
POLICY_PATH = Path("receipts/ext-064-production-policy-freeze.json")
IMPL_RECEIPT_PATH = Path("receipts/ext-065-reference-erc1155-implementation.json")
CONTRACT_PATH = Path("contracts/reference/EXT065ReferenceWitnessBadge.sol")

EXPECTED = {
    "issue": "EXT-066",
    "title": "Local Compile & Unit-Test Validation Gate",
    "depends_on": ["EXT-065"],
    "validation_mode": "local_compile_and_unit_test",
    "compile_validation_allowed": True,
    "unit_test_allowed": True,
    "compile_allowed": False,
    "deploy_allowed": False,
    "publish_allowed": False,
    "runtime_mode": "witness_only",
    "authority": False,
    "truth_claim": False,
    "resolution_semantics": "absent",
    "badge_power": 0,
    "vote_power": 0,
    "governance_action_allowed": False,
    "promotion_allowed": False,
    "transfer_governance_rights": False,
    "policy_source": "EXT-064",
}

POLICY_KEYS = [
    "runtime_mode",
    "authority",
    "truth_claim",
    "resolution_semantics",
    "badge_power",
    "vote_power",
    "governance_action_allowed",
    "promotion_allowed",
    "transfer_governance_rights",
]

SOURCE_REQUIRED = [
    "contract EXT065ReferenceWitnessBadge is ERC1155, Ownable",
    "POLICY_SOURCE = \"EXT-064\"",
    "RUNTIME_MODE = \"witness_only\"",
    "RESOLUTION_SEMANTICS = \"absent\"",
    "AUTHORITY = false",
    "TRUTH_CLAIM = false",
    "GOVERNANCE_ACTION_ALLOWED = false",
    "PROMOTION_ALLOWED = false",
    "TRANSFER_GOVERNANCE_RIGHTS = false",
    "RECEIPT_HASH_REQUIRED = true",
    "ONE_BADGE_PER_RECEIPT = true",
    "NON_TRANSFERABLE = true",
    "BADGE_POWER = 0",
    "VOTE_POWER = 0",
    "if (receiptHash == bytes32(0)) revert ReceiptHashRequired();",
    "if (!witnessCompletion) revert WitnessCompletionRequired();",
    "if (mintedReceipts[receiptHash]) revert DuplicateReceipt();",
    "revert NonTransferable();",
    "revert GovernanceDisabled();",
    "revert TruthPromotionDisabled();",
]

SOURCE_FORBIDDEN = [
    "AUTHORITY = true",
    "TRUTH_CLAIM = true",
    "GOVERNANCE_ACTION_ALLOWED = true",
    "PROMOTION_ALLOWED = true",
    "TRANSFER_GOVERNANCE_RIGHTS = true",
    "BADGE_POWER = 1",
    "VOTE_POWER = 1",
    "delegateVotePower",
    "settleOutcome",
    "claimTruth",
    "setAuthority",
]


def fail(message: str) -> None:
    print(f"EXT-066 FAIL: {message}")
    sys.exit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(obj: dict) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    for path in [RECEIPT_PATH, POLICY_PATH, IMPL_RECEIPT_PATH, CONTRACT_PATH]:
        require(path.exists(), f"missing required file: {path}")

    try:
        receipt = json.loads(RECEIPT_PATH.read_text())
        policy = json.loads(POLICY_PATH.read_text())
        impl_receipt = json.loads(IMPL_RECEIPT_PATH.read_text())
    except json.JSONDecodeError as exc:
        fail(f"invalid json: {exc}")

    for key, expected_value in EXPECTED.items():
        actual_value = receipt.get(key)
        require(actual_value == expected_value, f"{key}: expected {expected_value!r}, got {actual_value!r}")

    require(impl_receipt.get("issue") == "EXT-065", "implementation receipt must be EXT-065")
    require(impl_receipt.get("policy_source") == "EXT-064", "implementation must reference EXT-064")

    for key in POLICY_KEYS:
        require(receipt.get(key) == policy.get(key), f"EXT-066 policy mismatch for {key}")
        require(impl_receipt.get(key) == policy.get(key), f"EXT-065 policy mismatch for {key}")

    source = CONTRACT_PATH.read_text()

    for marker in SOURCE_REQUIRED:
        require(marker in source, f"missing source marker: {marker}")

    for marker in SOURCE_FORBIDDEN:
        require(marker not in source, f"forbidden source marker present: {marker}")

    require(source.count("revert NonTransferable();") >= 2, "both transfer functions must revert")
    require("function vote()" in source and "function resolve()" in source, "governance stubs must exist")
    require("function grantAuthority()" in source and "function promoteTruth()" in source, "authority/truth stubs must exist")

    require(receipt.get("compile_validation_allowed") is True, "compile validation readiness may be true")
    require(receipt.get("unit_test_allowed") is True, "unit test readiness may be true")
    require(receipt.get("compile_allowed") is False, "compile_allowed must remain false")
    require(receipt.get("deploy_allowed") is False, "release-to-chain must remain disabled")
    require(receipt.get("publish_allowed") is False, "publish_allowed must remain false")

    policy_digest = sha256_json(policy)
    implementation_digest = sha256_text(source)
    validation_digest = sha256_json({
        "receipt": receipt,
        "policy_digest": policy_digest,
        "implementation_digest": implementation_digest,
    })

    print("EXT-066 PASS: reference implementation validated; policy conformity verified; local compile/unit-test gate satisfied; compile/release remain disabled; authority=false; truth_claim=false; vote_power=0")
    print(f"EXT-066 POLICY DIGEST: sha256:{policy_digest}")
    print(f"EXT-066 IMPLEMENTATION DIGEST: sha256:{implementation_digest}")
    print(f"EXT-066 VALIDATION DIGEST: sha256:{validation_digest}")


if __name__ == "__main__":
    main()
