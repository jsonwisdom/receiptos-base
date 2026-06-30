#!/usr/bin/env python3
import hashlib
import json
import sys
from pathlib import Path

RECEIPT_PATH = Path("receipts/ext-067-testnet-readiness-review.json")
POLICY_PATH = Path("receipts/ext-064-production-policy-freeze.json")
IMPLEMENTATION_RECEIPT_PATH = Path("receipts/ext-065-reference-erc1155-implementation.json")
VALIDATION_RECEIPT_PATH = Path("receipts/ext-066-local-compile-unit-test-gate.json")
CONTRACT_PATH = Path("contracts/reference/EXT065ReferenceWitnessBadge.sol")

EXPECTED = {
    "issue": "EXT-067",
    "title": "Testnet Readiness Review",
    "depends_on": ["EXT-066"],
    "review_mode": "testnet_readiness_only",
    "deployment_authorized": False,
    "deployment_executed": False,
    "runtime_mode": "witness_only",
    "policy_source": "EXT-064",
    "implementation_source": "EXT-065",
    "validation_source": "EXT-066",
    "authority": False,
    "truth_claim": False,
    "resolution_semantics": "absent",
    "badge_power": 0,
    "vote_power": 0,
    "governance_action_allowed": False,
    "promotion_allowed": False,
    "transfer_governance_rights": False,
    "review_complete": True,
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

CONTRACT_REQUIRED = [
    "POLICY_SOURCE = \"EXT-064\"",
    "RUNTIME_MODE = \"witness_only\"",
    "AUTHORITY = false",
    "TRUTH_CLAIM = false",
    "BADGE_POWER = 0",
    "VOTE_POWER = 0",
    "RECEIPT_HASH_REQUIRED = true",
    "ONE_BADGE_PER_RECEIPT = true",
    "NON_TRANSFERABLE = true",
    "revert NonTransferable();",
    "revert GovernanceDisabled();",
    "revert TruthPromotionDisabled();",
]

CONTRACT_FORBIDDEN = [
    "AUTHORITY = true",
    "TRUTH_CLAIM = true",
    "BADGE_POWER = 1",
    "VOTE_POWER = 1",
    "delegateVotePower",
    "settleOutcome",
    "claimTruth",
    "setAuthority",
]


def fail(message: str) -> None:
    print(f"EXT-067 FAIL: {message}")
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
    for path in [RECEIPT_PATH, POLICY_PATH, IMPLEMENTATION_RECEIPT_PATH, VALIDATION_RECEIPT_PATH, CONTRACT_PATH]:
        require(path.exists(), f"missing required file: {path}")

    try:
        receipt = json.loads(RECEIPT_PATH.read_text())
        policy = json.loads(POLICY_PATH.read_text())
        implementation = json.loads(IMPLEMENTATION_RECEIPT_PATH.read_text())
        validation = json.loads(VALIDATION_RECEIPT_PATH.read_text())
    except json.JSONDecodeError as exc:
        fail(f"invalid json: {exc}")

    for key, expected_value in EXPECTED.items():
        actual_value = receipt.get(key)
        require(actual_value == expected_value, f"{key}: expected {expected_value!r}, got {actual_value!r}")

    require(policy.get("issue") == "EXT-064", "policy receipt must be EXT-064")
    require(implementation.get("issue") == "EXT-065", "implementation receipt must be EXT-065")
    require(validation.get("issue") == "EXT-066", "validation receipt must be EXT-066")

    for key in POLICY_KEYS:
        require(receipt.get(key) == policy.get(key), f"EXT-067 policy mismatch for {key}")
        require(implementation.get(key) == policy.get(key), f"EXT-065 policy mismatch for {key}")
        require(validation.get(key) == policy.get(key), f"EXT-066 policy mismatch for {key}")

    require(receipt.get("deployment_authorized") is False, "deployment_authorized must remain false")
    require(receipt.get("deployment_executed") is False, "deployment_executed must remain false")
    require(receipt.get("review_complete") is True, "review_complete must be true")

    source = CONTRACT_PATH.read_text()
    for marker in CONTRACT_REQUIRED:
        require(marker in source, f"missing contract marker: {marker}")

    for marker in CONTRACT_FORBIDDEN:
        require(marker not in source, f"forbidden contract marker present: {marker}")

    policy_digest = sha256_json(policy)
    implementation_digest = sha256_text(source)
    validation_digest = sha256_json(validation)
    readiness_digest = sha256_json({
        "receipt": receipt,
        "policy_digest": policy_digest,
        "implementation_digest": implementation_digest,
        "validation_digest": validation_digest,
    })

    print("EXT-067 PASS: testnet readiness reviewed; policy conformity preserved; deployment not authorized; deployment not executed; witness membrane intact; authority=false; truth_claim=false; vote_power=0")
    print(f"EXT-067 POLICY DIGEST: sha256:{policy_digest}")
    print(f"EXT-067 IMPLEMENTATION DIGEST: sha256:{implementation_digest}")
    print(f"EXT-067 VALIDATION DIGEST: sha256:{validation_digest}")
    print(f"EXT-067 READINESS DIGEST: sha256:{readiness_digest}")


if __name__ == "__main__":
    main()
