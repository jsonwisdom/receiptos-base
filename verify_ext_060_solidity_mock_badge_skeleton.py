#!/usr/bin/env python3
import json
import sys
from pathlib import Path

RECEIPT_PATH = Path("receipts/ext-060-solidity-mock-badge-skeleton.json")

EXPECTED = {
    "issue": "EXT-060",
    "title": "Solidity Mock Badge Contract Skeleton",
    "status": "MOCK_SOLIDITY_SKELETON_LOCKED",
    "depends_on": ["EXT-058", "EXT-059"],
    "contract_path": "contracts/mock/EXT060MockWitnessBadge.sol",
    "contract_mode": "mock_skeleton_only",
    "deploy_allowed": False,
    "standard_model": "ERC-1155-style",
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

FORBIDDEN_SOLIDITY_SNIPPETS = [
    "DEPLOY_ALLOWED = true",
    "AUTHORITY = true",
    "TRUTH_CLAIM = true",
    "GOVERNANCE_ACTION_ALLOWED = true",
    "TRANSFER_GOVERNANCE_RIGHTS = true",
    "PROMOTION_ALLOWED = true",
    "BADGE_POWER = 1",
    "VOTE_POWER = 1",
    "delegateVotePower",
    "settleOutcome",
]


def fail(message: str) -> None:
    print(f"EXT-060 FAIL: {message}")
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

    contract_path = Path(receipt["contract_path"])
    if not contract_path.exists():
        fail(f"missing contract skeleton: {contract_path}")

    source = contract_path.read_text()

    required_markers = receipt.get("required_solidity_markers")
    if not isinstance(required_markers, list) or not required_markers:
        fail("required_solidity_markers must be a non-empty list")

    for marker in required_markers:
        if marker not in source:
            fail(f"missing Solidity marker: {marker}")

    for snippet in FORBIDDEN_SOLIDITY_SNIPPETS:
        if snippet in source:
            fail(f"forbidden Solidity snippet present: {snippet}")

    required_functions = [
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

    for function_marker in required_functions:
        if function_marker not in source:
            fail(f"missing required function marker: {function_marker}")

    if "constructor()" not in source or "revert MockOnlyNoDeployAuthority();" not in source:
        fail("constructor must revert with MockOnlyNoDeployAuthority")

    if source.count("revert TransferDisabled();") < 2:
        fail("both transfer functions must revert TransferDisabled")

    if "receiptHash == bytes32(0)" not in source:
        fail("receipt hash zero check required")

    if "receiptMinted[receiptHash]" not in source:
        fail("oneBadgePerReceipt receiptMinted guard required")

    print("EXT-060 PASS: Solidity mock badge skeleton locked; no deploy, non-transferable, receipt-tied, zero power, no authority")


if __name__ == "__main__":
    main()
