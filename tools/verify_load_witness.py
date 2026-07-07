#!/usr/bin/env python3
"""Signed receipt and transparency verifier v0.1.

This verifier is independent from the load runner. It never trusts runner status
alone. It checks witness schema, receipt digest, Ed25519 signature verification,
transparency continuity, and doctrine guards before allowing a LOAD_VERIFIED result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import jsonschema
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
except ImportError as exc:  # pragma: no cover
    raise SystemExit(f"missing dependency: {exc}")

HEX_64 = re.compile(r"^[a-f0-9]{64}$")
HEX_40 = re.compile(r"^[a-f0-9]{40}$")
HEX_128 = re.compile(r"^[a-f0-9]{128}$")

SENTINEL_SHA256 = {
    "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "0" * 64,
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fail(code: str) -> None:
    raise SystemExit(code)


def require(condition: bool, code: str) -> None:
    if not condition:
        fail(code)


def validate_schema(witness: dict[str, Any], schema: dict[str, Any]) -> None:
    try:
        jsonschema.Draft202012Validator(schema).validate(witness)
    except jsonschema.ValidationError as exc:
        fail(f"INVALID_WITNESS_SCHEMA: {exc.message}")


def witness_signing_payload(witness: dict[str, Any]) -> str:
    core = dict(witness)
    core.pop("signature", None)
    return canonical_json(core)


def verify_receipt_digest(witness: dict[str, Any]) -> bool:
    integrity = witness["receipt_integrity"]
    receipt_sha = integrity["receipt_sha256"]
    require(receipt_sha not in SENTINEL_SHA256, "SENTINEL_RECEIPT_DIGEST")
    core = dict(witness)
    core.pop("receipt_integrity", None)
    core.pop("signature", None)
    computed = sha256_text(canonical_json(core))
    return computed == receipt_sha


def verify_ed25519_signature(witness: dict[str, Any]) -> bool:
    signature = witness.get("signature")
    if not isinstance(signature, dict):
        return False
    if signature.get("alg") != "Ed25519":
        return False

    public_key_hex = signature.get("public_key")
    signature_hex = signature.get("signature")
    if not isinstance(public_key_hex, str) or not HEX_64.match(public_key_hex):
        return False
    if not isinstance(signature_hex, str) or not HEX_128.match(signature_hex):
        return False

    try:
        public_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
        public_key.verify(bytes.fromhex(signature_hex), witness_signing_payload(witness).encode("utf-8"))
        return True
    except (ValueError, InvalidSignature):
        return False


def verify_signature_fields(witness: dict[str, Any]) -> bool:
    return witness["receipt_integrity"].get("signature_verified") is True and verify_ed25519_signature(witness)


def verify_transparency(witness: dict[str, Any], transparency_log: dict[str, Any], chain_head: dict[str, Any]) -> bool:
    tc = witness["transparency_continuity"]
    require(bool(HEX_40.match(tc["chain_head"])), "INVALID_CHAIN_HEAD_SHAPE")
    require(bool(HEX_40.match(tc["merged_public_surface_sha"])), "INVALID_PUBLIC_SURFACE_SHA")
    require(bool(HEX_40.match(tc["continuous_from"])), "INVALID_CONTINUITY_BASE")

    return (
        transparency_log.get("run_id") == witness["run_id"]
        and transparency_log.get("status") == witness["gate_result"]["status"]
        and chain_head.get("latest_run_id") == witness["run_id"]
        and chain_head.get("latest_status") == witness["gate_result"]["status"]
        and chain_head.get("chain_head") == tc["chain_head"]
    )


def verify_doctrine(witness: dict[str, Any]) -> bool:
    guards = witness["doctrine_guards"]
    return (
        witness["transform_version_pinned"] is True
        and witness["membrane_unchanged"] is True
        and guards["authority_false"] is True
        and guards["no_fake_green"] is True
        and guards["no_synthetic_pass"] is True
        and guards["no_public_load_badge_before_witness"] is True
    )


def verify_witness(witness: dict[str, Any], schema: dict[str, Any], transparency_log: dict[str, Any], chain_head: dict[str, Any]) -> dict[str, Any]:
    validate_schema(witness, schema)

    checks = {
        "receipt_digest_match": verify_receipt_digest(witness),
        "signature_valid": verify_signature_fields(witness),
        "hash_chain_continuous": verify_transparency(witness, transparency_log, chain_head),
        "doctrine_guards_pass": verify_doctrine(witness),
        "failed_conditions_empty": witness["failed_conditions"] == [],
    }

    promoted = all(checks.values()) and witness["gate_result"]["status"] == "LOAD_VERIFIED"
    return {
        "verifier_version": "SIGNED_LOAD_RECEIPT_VERIFIER_V0_1",
        "run_id": witness["run_id"],
        "status": "LOAD_VERIFIED" if promoted else "GOVERNANCE_GAP",
        "checks": checks,
        "canonical_digest": sha256_text(canonical_json(witness)),
        "authority": False,
        "no_fake_green": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify load witness, transparency log, and chain head.")
    parser.add_argument("--witness", required=True)
    parser.add_argument("--transparency-log", required=True)
    parser.add_argument("--chain-head", required=True)
    parser.add_argument("--schema", default="schemas/LOAD_VERIFICATION_WITNESS_V0_1.schema.json")
    parser.add_argument("--out", default="artifacts/load-witness-verification.json")
    parser.add_argument("--allow-governance-gap-exit-zero", action="store_true")
    args = parser.parse_args()

    witness = load_json(Path(args.witness))
    schema = load_json(Path(args.schema))
    transparency_log = load_json(Path(args.transparency_log))
    chain_head = load_json(Path(args.chain_head))

    result = verify_witness(witness, schema, transparency_log, chain_head)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))

    if result["status"] == "LOAD_VERIFIED":
        return 0
    return 0 if args.allow_governance_gap_exit_zero else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit as exc:
        if exc.code not in (0, None):
            print(exc.code, file=sys.stderr)
        raise
