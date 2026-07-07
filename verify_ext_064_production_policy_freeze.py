#!/usr/bin/env python3
import hashlib
import json
import sys
from pathlib import Path

RECEIPT_PATH = Path("receipts/ext-064-production-policy-freeze.json")

EXPECTED = {
    "issue": "EXT-064",
    "title": "Production Policy Freeze",
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
    "production_policy_frozen": True,
}


def fail(message: str) -> None:
    print(f"EXT-064 FAIL: {message}")
    sys.exit(1)


def canonical_digest(receipt: dict) -> str:
    payload = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    if not RECEIPT_PATH.exists():
        fail(f"missing receipt: {RECEIPT_PATH}")

    try:
        receipt = json.loads(RECEIPT_PATH.read_text())
    except json.JSONDecodeError as exc:
        fail(f"invalid json: {exc}")

    if set(receipt.keys()) != set(EXPECTED.keys()):
        extra = sorted(set(receipt.keys()) - set(EXPECTED.keys()))
        missing = sorted(set(EXPECTED.keys()) - set(receipt.keys()))
        fail(f"unexpected policy keyset; extra={extra!r}; missing={missing!r}")

    for key, expected_value in EXPECTED.items():
        actual_value = receipt.get(key)
        if actual_value != expected_value:
            fail(f"{key}: expected {expected_value!r}, got {actual_value!r}")

    if receipt["authority"] is not False:
        fail("authority must remain false")

    if receipt["truth_claim"] is not False:
        fail("truth_claim must remain false")

    if receipt["governance_action_allowed"] is not False:
        fail("governance_action_allowed must remain false")

    if receipt["promotion_allowed"] is not False:
        fail("promotion_allowed must remain false")

    if receipt["transfer_governance_rights"] is not False:
        fail("transfer_governance_rights must remain false")

    if receipt["badge_power"] != 0 or receipt["vote_power"] != 0:
        fail("badge_power and vote_power must remain zero")

    if receipt["receiptHashRequired"] is not True:
        fail("receiptHashRequired must remain true")

    if receipt["oneBadgePerReceipt"] is not True:
        fail("oneBadgePerReceipt must remain true")

    if receipt["nonTransferable"] is not True:
        fail("nonTransferable must remain true")

    if receipt["production_policy_frozen"] is not True:
        fail("production_policy_frozen must remain true")

    digest = canonical_digest(receipt)
    print("EXT-064 PASS: production policy frozen; implementation-independent invariants verified; witness membrane preserved; ready for future implementations")
    print(f"EXT-064 POLICY DIGEST: sha256:{digest}")


if __name__ == "__main__":
    main()
