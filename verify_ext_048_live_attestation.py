#!/usr/bin/env python3
import json
import sys
from pathlib import Path

RECEIPT_PATH = Path("receipts/ext-048-live-attestation.json")

EXPECTED = {
    "issue": "EXT-048",
    "title": "Live Base EAS Attestation Capture",
    "status": "ANCHORED",
    "network": "Base",
    "transaction_hash": "0xc5e4ab69f766bdec8b156ff1bdb0c2f4fd9807214dce9d23494750796a90e4de",
    "attestation_uid": "0x917443357fbcfcc3ed7e684f84b1fb2905f09ea0fae67965f57f55f2ff5ef8be",
    "schema_uid": "0x507ddacbafa541960018b930850b5d31a5828d317ee9c0a5851a96e954bc553c",
    "anchored_payload": "EXT-048 payload",
    "payload_hash": "ec367705093513fdb6efd12122f0c4d79aa51fd687f0f85966b86e1f07e40922",
    "payload_path": "receipts/ext-044-eas-anchor-payload.json",
    "commit": "722eca5",
    "tag": "ext-047-base-eas-submitted",
    "authority": False,
    "resolution_semantics": "absent",
    "truth_claim": False,
}


def fail(message: str) -> None:
    print(f"EXT-048 FAIL: {message}")
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

    if receipt.get("authority") is not False:
        fail("authority must be false")

    if receipt.get("truth_claim") is not False:
        fail("truth_claim must be false")

    if receipt.get("resolution_semantics") != "absent":
        fail("resolution_semantics must be absent")

    print("EXT-048 PASS: live Base EAS attestation captured; authority=false; truth_claim=false")


if __name__ == "__main__":
    main()
