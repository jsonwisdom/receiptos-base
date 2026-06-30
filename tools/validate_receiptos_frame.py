#!/usr/bin/env python3
"""ReceiptOS / ESG-001 wire-native frame validator.

This validator intentionally stops at the representation layer:
canonical JSON bytes, SHA-256 frame-payload binding, timestamp bounds,
nonce structure, signature envelope shape, and explicit authority=false /
truth_claim=false.

It does not infer truth, causation, confidence, admissibility, graph state,
or crypto-policy validity. Algorithm-specific signature verification belongs
in conformance profiles above the base ReceiptOS / ESG-001 layer.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

HASH_RE = re.compile(r"^sha256:[a-f0-9]{64}$")
BASE64_RE = re.compile(r"^[A-Za-z0-9+/]*={0,2}$")
SUPPORTED_HASHES = {"sha256"}


def canonical_json_bytes(value: Any) -> bytes:
    """Return deterministic UTF-8 JSON bytes for conformance hashing."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_uri(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def parse_time(value: str) -> dt.datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = dt.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return parsed.astimezone(dt.timezone.utc)


def validate_signature_envelope(signature: Any) -> tuple[bool, list[str]]:
    """Validate signature envelope hygiene without crypto-policy enforcement."""
    errors: list[str] = []
    if not isinstance(signature, dict):
        return False, ["signature_must_be_object"]

    allowed = {"key_id", "signature_bytes", "profile"}
    for key in signature:
        if key not in allowed:
            errors.append(f"signature_unexpected_field:{key}")

    key_id = signature.get("key_id")
    if not isinstance(key_id, str) or not key_id:
        errors.append("signature_key_id_invalid")

    signature_bytes = signature.get("signature_bytes")
    if not isinstance(signature_bytes, str) or not BASE64_RE.match(signature_bytes):
        errors.append("signature_bytes_invalid_base64_shape")

    profile = signature.get("profile")
    if profile is not None and (not isinstance(profile, str) or not profile):
        errors.append("signature_profile_invalid")

    return not errors, errors


def validate_frame(frame: dict[str, Any], max_skew_seconds: int) -> dict[str, Any]:
    required = [
        "protocol", "version", "frame_type", "signature_domain", "payload_hash",
        "hash_algorithm", "signature_algorithm", "signer", "timestamp", "nonce",
        "payload", "signature", "authority", "truth_claim",
    ]

    errors: list[str] = []
    for key in required:
        if key not in frame:
            errors.append(f"missing_required_field:{key}")

    valid_encoding = isinstance(frame, dict)
    if frame.get("protocol") != "ReceiptOS":
        errors.append("invalid_protocol")
    if frame.get("authority") is not False:
        errors.append("authority_must_be_false")
    if frame.get("truth_claim") is not False:
        errors.append("truth_claim_must_be_false")

    hash_algorithm = frame.get("hash_algorithm")
    if hash_algorithm not in SUPPORTED_HASHES:
        errors.append("unsupported_hash_algorithm")

    declared_hash = frame.get("payload_hash")
    if not isinstance(declared_hash, str) or not HASH_RE.match(declared_hash):
        errors.append("invalid_payload_hash_format")

    declared_nonce = frame.get("nonce")
    nonce_well_formed = isinstance(declared_nonce, str) and bool(HASH_RE.match(declared_nonce))
    if not nonce_well_formed:
        errors.append("invalid_nonce_format")

    signature_algorithm = frame.get("signature_algorithm")
    if not isinstance(signature_algorithm, str) or not signature_algorithm:
        errors.append("signature_algorithm_invalid")

    payload = frame.get("payload")
    hash_match = False
    if isinstance(payload, dict) and isinstance(declared_hash, str):
        computed = sha256_uri(canonical_json_bytes(payload))
        hash_match = computed == declared_hash
        if not hash_match:
            errors.append("payload_hash_mismatch")
    else:
        errors.append("payload_must_be_object")

    timestamp_within_bounds = False
    try:
        ts = parse_time(str(frame.get("timestamp")))
        now = dt.datetime.now(dt.timezone.utc)
        timestamp_within_bounds = abs((now - ts).total_seconds()) <= max_skew_seconds
        if not timestamp_within_bounds:
            errors.append("timestamp_out_of_bounds")
    except Exception:
        errors.append("invalid_timestamp")

    signature_envelope_valid, signature_errors = validate_signature_envelope(frame.get("signature"))
    errors.extend(signature_errors)

    conformant = not errors
    return {
        "valid_encoding": valid_encoding,
        "hash_match": hash_match,
        "signature_envelope_valid": signature_envelope_valid,
        "timestamp_within_bounds": timestamp_within_bounds,
        "nonce_well_formed": nonce_well_formed,
        "conformant": conformant,
        "authority": False,
        "truth_claim": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a ReceiptOS / ESG-001 frame.")
    parser.add_argument("frame", type=Path)
    parser.add_argument("--max-skew-seconds", type=int, default=300)
    args = parser.parse_args()

    frame = json.loads(args.frame.read_text(encoding="utf-8"))
    result = validate_frame(frame, args.max_skew_seconds)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["conformant"] else 1


if __name__ == "__main__":
    sys.exit(main())
