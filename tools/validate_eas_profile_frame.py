#!/usr/bin/env python3
"""ReceiptOS EAS v1 profile validator.

This script composes above the base ReceiptOS / ESG-001 validator.
It first verifies base representation conformance, then checks only EAS
profile shape. It does not perform on-chain lookup, truth adjudication,
legal classification, or EAS contract verification.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from validate_receiptos_frame import validate_frame

HEX32_RE = re.compile(r"^0x[a-fA-F0-9]{64}$")
ADDR_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
SHA256_URI_RE = re.compile(r"^sha256:[a-f0-9]{64}$")


def validate_eas_profile(frame: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    payload = frame.get("payload")
    signature = frame.get("signature")

    if not isinstance(payload, dict):
        errors.append("payload_must_be_object")
        payload = {}

    if payload.get("profile") != "receiptos-eas-v1":
        errors.append("payload_profile_must_be_receiptos_eas_v1")

    artifact_hash = payload.get("artifact_hash")
    if not isinstance(artifact_hash, str) or not SHA256_URI_RE.match(artifact_hash):
        errors.append("artifact_hash_invalid_shape")

    if payload.get("artifact_hash_role") != "opaque_profile_claim":
        errors.append("artifact_hash_role_must_be_opaque_profile_claim")

    eas = payload.get("eas")
    if not isinstance(eas, dict):
        errors.append("eas_must_be_object")
        eas = {}

    if not isinstance(eas.get("chain_id"), int) or eas.get("chain_id") < 1:
        errors.append("eas_chain_id_invalid")

    for key in ("schema_uid", "attestation_uid", "tx_hash"):
        value = eas.get(key)
        if not isinstance(value, str) or not HEX32_RE.match(value):
            errors.append(f"eas_{key}_invalid")

    contract = eas.get("contract")
    if contract is not None and (not isinstance(contract, str) or not ADDR_RE.match(contract)):
        errors.append("eas_contract_invalid")

    if not isinstance(signature, dict) or signature.get("profile") != "eas-attestation-v1":
        errors.append("signature_profile_must_be_eas_attestation_v1")

    return {
        "eas_profile_valid": not errors,
        "authority": False,
        "truth_claim": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ReceiptOS + EAS v1 profile shape.")
    parser.add_argument("frame", type=Path)
    parser.add_argument("--max-skew-seconds", type=int, default=300)
    parser.add_argument(
        "--disable-timestamp",
        action="store_true",
        help="Bypass timestamp freshness check for deterministic fixtures.",
    )
    args = parser.parse_args()

    frame = json.loads(args.frame.read_text(encoding="utf-8"))
    base = validate_frame(frame, args.max_skew_seconds, args.disable_timestamp)
    profile = validate_eas_profile(frame)
    result = {
        "base_conformant": base["conformant"],
        "eas_profile_valid": profile["eas_profile_valid"],
        "conformant": base["conformant"] and profile["eas_profile_valid"],
        "authority": False,
        "truth_claim": False,
        "base_errors": base["errors"],
        "profile_errors": profile["errors"],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["conformant"] else 1


if __name__ == "__main__":
    sys.exit(main())
