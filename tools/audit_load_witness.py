#!/usr/bin/env python3
"""Audit LOAD_VERIFICATION_WITNESS_V0_1 claims.

This guard exists to prevent narrative promotion from malformed or placeholder
artifacts. It is intentionally stricter for LOAD_VERIFIED than for ordinary
GOVERNANCE_GAP harness output.
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
except ImportError as exc:  # pragma: no cover
    raise SystemExit(f"missing dependency: {exc}")

SENTINEL_SHA256 = {
    "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",  # sha256('test')
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # sha256(empty)
    "0" * 64,
}

HEX_64 = re.compile(r"^[a-f0-9]{64}$")
HEX_40 = re.compile(r"^[a-f0-9]{40}$")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fail(code: str) -> None:
    raise SystemExit(code)


def require(condition: bool, code: str) -> None:
    if not condition:
        fail(code)


def audit_claim(witness: dict[str, Any], schema: dict[str, Any]) -> None:
    # First enforce the locked schema. This rejects string placeholders like
    # receipt_integrity='PASS' and transparency_continuity='PASS'.
    try:
        jsonschema.Draft202012Validator(schema).validate(witness)
    except jsonschema.ValidationError as exc:
        fail(f"INVALID_SCHEMA: {exc.message}")

    gate = witness["gate_result"]
    if gate["status"] != "LOAD_VERIFIED":
        print("GOVERNANCE_GAP_OR_NON_LOAD_STATUS")
        return

    require(witness["failed_conditions"] == [], "LOAD_VERIFIED_WITH_FAILED_CONDITIONS")
    require(witness["transform_version_pinned"] is True, "TRANSFORM_VERSION_NOT_PINNED")
    require(witness["membrane_unchanged"] is True, "MEMBRANE_CHANGED")

    integrity = witness["receipt_integrity"]
    receipt_sha = integrity["receipt_sha256"]
    require(bool(HEX_64.match(receipt_sha)), "INVALID_RECEIPT_SHA256_SHAPE")
    require(receipt_sha not in SENTINEL_SHA256, "SENTINEL_RECEIPT_DIGEST")
    require(integrity["jcs_canonical"] is True, "NON_CANONICAL_RECEIPT")
    require(integrity["signature_verified"] is True, "UNSIGNED_RECEIPT")

    continuity = witness["transparency_continuity"]
    require(bool(HEX_40.match(continuity["chain_head"])), "INVALID_CHAIN_HEAD_SHAPE")
    require(bool(HEX_40.match(continuity["merged_public_surface_sha"])), "INVALID_PUBLIC_SURFACE_SHA")
    require(bool(HEX_40.match(continuity["continuous_from"])), "INVALID_CONTINUITY_BASE")

    doctrine = witness["doctrine_guards"]
    for key in (
        "authority_false",
        "no_fake_green",
        "no_synthetic_pass",
        "no_public_load_badge_before_witness",
    ):
        require(doctrine[key] is True, f"DOCTRINE_GUARD_FALSE:{key}")

    # Optional self-consistency check: if receipt_sha256 is meant to cover the
    # witness body excluding receipt_integrity, enforce it. This blocks arbitrary
    # pasted digests while keeping the rule deterministic.
    core = dict(witness)
    core.pop("receipt_integrity", None)
    computed = sha256_hex_text(canonical_json(core))
    require(receipt_sha == computed, "RECEIPT_DIGEST_MISMATCH")

    print("LOAD_VERIFIED_AUDIT_PASS")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a load verification witness claim.")
    parser.add_argument("witness")
    parser.add_argument(
        "--schema",
        default="schemas/LOAD_VERIFICATION_WITNESS_V0_1.schema.json",
    )
    args = parser.parse_args()

    witness = load_json(Path(args.witness))
    schema = load_json(Path(args.schema))
    require(isinstance(witness, dict), "WITNESS_NOT_OBJECT")
    require(isinstance(schema, dict), "SCHEMA_NOT_OBJECT")
    audit_claim(witness, schema)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit as exc:
        if exc.code not in (0, None):
            print(exc.code, file=sys.stderr)
        raise
