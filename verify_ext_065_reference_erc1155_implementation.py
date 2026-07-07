#!/usr/bin/env python3
import hashlib
import json
import sys
from pathlib import Path

RECEIPT_PATH = Path("receipts/ext-065-reference-erc1155-implementation.json")
POLICY_PATH = Path("receipts/ext-064-production-policy-freeze.json")

EXPECTED = {
    "issue": "EXT-065",
    "title": "Reference ERC-1155 Implementation",
    "status": "REFERENCE_IMPLEMENTATION_LOCKED",
    "depends_on": ["EXT-064"],
    "contract_path": "contracts/reference/EXT065ReferenceWitnessBadge.sol",
    "policy_source": "EXT-064",
    "contract_mode": "reference_implementation",
    "runtime_mode": "witness_only",
    "authority": False,
    "truth_claim": False,
    "resolution_semantics": "absent",
    "badge_power": 0,
    "vote_power": 0,
    "governance_action_allowed": False,
    "promotion_allowed": False,
    "transfer_governance_rights": False,
    "receiptHashRequired": True,
    "oneBadgePerReceipt": True,
    "nonTransferable": True,
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
    "receiptHashRequired",
    "oneBadgePerReceipt",
    "nonTransferable",
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
    "mintedReceipts[receiptHash] = true;",
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
    "RECEIPT_HASH_REQUIRED = false",
    "ONE_BADGE_PER_RECEIPT = false",
    "NON_TRANSFERABLE = false",
    "BADGE_POWER = 1",
    "VOTE_POWER = 1",
    "delegateVotePower",
    "settleOutcome",
    "claimTruth",
    "setAuthority",
]


def fail(message: str) -> None:
    print(f"EXT-065 FAIL: {message}")
    sys.exit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> None:
    require(RECEIPT_PATH.exists(), f"missing receipt: {RECEIPT_PATH}")
    require(POLICY_PATH.exists(), f"missing policy freeze: {POLICY_PATH}")

    try:
        receipt = json.loads(RECEIPT_PATH.read_text())
        policy = json.loads(POLICY_PATH.read_text())
    except json.JSONDecodeError as exc:
        fail(f"invalid json: {exc}")

    for key, expected_value in EXPECTED.items():
        actual_value = receipt.get(key)
        require(actual_value == expected_value, f"{key}: expected {expected_value!r}, got {actual_value!r}")

    for key in POLICY_KEYS:
        require(receipt.get(key) == policy.get(key), f"policy mismatch for {key}: receipt={receipt.get(key)!r}, policy={policy.get(key)!r}")

    contract_path = Path(receipt["contract_path"])
    require(contract_path.exists(), f"missing contract: {contract_path}")

    source = contract_path.read_text()

    for marker in SOURCE_REQUIRED:
        require(marker in source, f"missing source marker: {marker}")

    for marker in SOURCE_FORBIDDEN:
        require(marker not in source, f"forbidden source marker present: {marker}")

    require(source.count("revert NonTransferable();") >= 2, "both transfer paths must revert NonTransferable")
    require("function vote()" in source and "function resolve()" in source, "governance stubs must exist and revert")
    require("function grantAuthority()" in source and "function promoteTruth()" in source, "authority/truth stubs must exist and revert")

    digest = sha256_text(source)
    print("EXT-065 PASS: reference implementation conforms to EXT-064 policy; witness-only semantics preserved; receipt-tied non-transferable badges; no vote; no authority; no truth promotion")
    print(f"EXT-065 IMPLEMENTATION DIGEST: sha256:{digest}")


if __name__ == "__main__":
    main()
