#!/usr/bin/env python3
import json
import sys
from pathlib import Path

RECEIPT_PATH = Path("receipts/ext-059-mock-mint-flow-test-vectors.json")

EXPECTED = {
    "issue": "EXT-059",
    "title": "Mock Mint Flow Test Vectors",
    "status": "MOCK_MINT_FLOW_VECTORS_LOCKED",
    "depends_on": ["EXT-057", "EXT-058"],
    "contract_mode": "mock_semantics_only",
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

ALLOWED_ACTIONS = {"Inspect", "Replay", "Verify", "Challenge", "Trace"}
FORBIDDEN_ACTIONS = {"Vote", "Resolve", "Promote Truth", "Grant Authority", "Execute Governance", "Settle Outcome"}
TRANSFER_ACTIONS = {"Transfer", "safeTransferFrom", "safeBatchTransferFrom"}
DEPLOY_ACTIONS = {"Deploy", "LiveDeploy"}


def fail(message: str) -> None:
    print(f"EXT-059 FAIL: {message}")
    sys.exit(1)


def expected_outcome(vector: dict) -> str:
    action = vector.get("action")

    if action in TRANSFER_ACTIONS:
        return "TRANSFER_REVERTS"

    if action in DEPLOY_ACTIONS:
        return "DEPLOY_REJECTED"

    if action in FORBIDDEN_ACTIONS:
        return "MINT_REJECTED"

    if action not in ALLOWED_ACTIONS:
        return "MINT_REJECTED"

    if vector.get("receipt_hash_present") is not True:
        return "MINT_REJECTED"

    if vector.get("witness_completion") is not True:
        return "MINT_REJECTED"

    if vector.get("duplicate_receipt") is True:
        return "MINT_REJECTED"

    return "MINT_ALLOWED"


def validate_vector(vector: dict, expected_kind: str) -> None:
    vector_id = vector.get("id")
    if not vector_id:
        fail("vector missing id")

    actual = expected_outcome(vector)
    declared = vector.get("expected")

    if actual != declared:
        fail(f"{vector_id}: declared {declared!r}, computed {actual!r}")

    if expected_kind == "valid" and actual != "MINT_ALLOWED":
        fail(f"{vector_id}: valid vector must mint")

    if expected_kind == "invalid" and actual == "MINT_ALLOWED":
        fail(f"{vector_id}: invalid vector must not mint")


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

    valid_vectors = receipt.get("valid_vectors")
    invalid_vectors = receipt.get("invalid_vectors")

    if not isinstance(valid_vectors, list) or not valid_vectors:
        fail("valid_vectors must be a non-empty list")

    if not isinstance(invalid_vectors, list) or not invalid_vectors:
        fail("invalid_vectors must be a non-empty list")

    ids = set()
    for vector in valid_vectors + invalid_vectors:
        vector_id = vector.get("id")
        if vector_id in ids:
            fail(f"duplicate vector id: {vector_id}")
        ids.add(vector_id)

    for vector in valid_vectors:
        validate_vector(vector, "valid")

    for vector in invalid_vectors:
        validate_vector(vector, "invalid")

    if receipt.get("deploy_allowed") is not False:
        fail("deploy_allowed must remain false")

    if receipt.get("badge_power") != 0 or receipt.get("vote_power") != 0:
        fail("badge_power and vote_power must remain zero")

    if receipt.get("authority") is not False or receipt.get("truth_claim") is not False:
        fail("authority and truth_claim must remain false")

    if receipt.get("governance_action_allowed") is not False:
        fail("mock mint flow must not allow governance action")

    if receipt.get("transfer_governance_rights") is not False:
        fail("mock mint flow must not transfer governance rights")

    if receipt.get("promotion_allowed") is not False:
        fail("mock mint flow must not allow truth promotion")

    print("EXT-059 PASS: mock mint vectors verified; valid witness completion mints only; invalid, transfer, deploy, vote, and truth paths blocked")


if __name__ == "__main__":
    main()
