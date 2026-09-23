#!/usr/bin/env python3
"""Offline bridge from ReceiptOS receipt cores to Base EAS schema #1797.

This module does not sign, submit, mutate parent artifacts, or fetch chain state.
It imports the canonical ReceiptOS hash rail from receiptos/core/hash.py, rejects
floats before hashing, verifies optional sealed artifacts by SHA-256, and emits
a deterministic payload for the externally verified EAS schema #1797.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any, Dict, Iterable, List, Tuple

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from receiptos.core.hash import canonical_json, canonical_receipt_hash, receipt_core

EAS_SCHEMA_NUMBER = 1797
EAS_SCHEMA_UID = "0xc90097ca9f787edcc5fa2ce0920032abe4c4417cc8356198fa12d397c46a453c"
CHAIN_ID = 8453
ZERO_BYTES32 = "0x" + ("00" * 32)

EVIDENCE_STATE = {
    "UNRESOLVED": 0,
    "PARTIAL": 1,
    "MATCH": 2,
    "NOT_APPLICABLE": 3,
}

RETRIEVAL_STATE = {
    "COMPLETE": 0,
    "FAILED": 1,
    "AUTH_BLOCKED": 2,
    "BUDGET_EXHAUSTED": 3,
    "NOT_ATTEMPTED": 4,
}


class BridgeError(RuntimeError):
    pass


def reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise BridgeError(f"FLOATS_PROHIBITED path={path}")
    if isinstance(value, list):
        for index, item in enumerate(value):
            reject_floats(item, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            reject_floats(item, f"{path}.{key}")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def bytes32_from_hex(value: str, field: str) -> str:
    if value.startswith("sha256:"):
        value = value[7:]
    if value.startswith("0x"):
        value = value[2:]
    value = value.lower()
    if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise BridgeError(f"INVALID_BYTES32 field={field} value={value}")
    return "0x" + value


def hash_canonical(value: Any) -> str:
    reject_floats(value)
    rendered = canonical_json(value).encode("utf-8")
    return "0x" + sha256_bytes(rendered)


def parse_state(value: str, mapping: Dict[str, int], field: str) -> int:
    upper = value.upper()
    if upper in mapping:
        return mapping[upper]
    try:
        numeric = int(value)
    except ValueError as exc:
        raise BridgeError(f"UNKNOWN_ENUM_VALUE field={field} value={value}") from exc
    if numeric not in mapping.values():
        raise BridgeError(f"UNKNOWN_ENUM_VALUE field={field} value={value}")
    return numeric


def verify_artifacts(items: Iterable[Tuple[str, str]]) -> List[Dict[str, Any]]:
    verified: List[Dict[str, Any]] = []
    for raw_path, expected in items:
        path = pathlib.Path(raw_path)
        if not path.is_file():
            raise BridgeError(f"ARTIFACT_MISSING path={path}")
        expected_hex = bytes32_from_hex(expected, f"artifact:{path}")[2:]
        actual = sha256_bytes(path.read_bytes())
        if actual != expected_hex:
            raise BridgeError(
                f"ARTIFACT_HASH_MISMATCH path={path} expected={expected_hex} actual={actual}"
            )
        verified.append({"path": str(path), "sha256": actual, "bytes": path.stat().st_size})
    return verified


def load_receipt(path: pathlib.Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BridgeError(f"INVALID_RECEIPT_JSON path={path} error={exc}") from exc
    if not isinstance(value, dict):
        raise BridgeError("RECEIPT_MUST_BE_OBJECT")
    reject_floats(value)
    if "subject" not in value:
        raise BridgeError("SUBJECT_MISSING")
    return value


def build_payload(
    receipt: Dict[str, Any],
    *,
    lineage_id: str,
    previous_receipt_hash: str,
    authority_chain: str,
    official_ref: str,
    created_at: int,
    evidence_state: int,
    retrieval_state: int,
    verified_artifacts: List[Dict[str, Any]],
) -> Dict[str, Any]:
    if not isinstance(created_at, int) or isinstance(created_at, bool) or not (0 <= created_at < 2**64):
        raise BridgeError(f"INVALID_UINT64 field=created_at value={created_at}")

    core = receipt_core(receipt)
    reject_floats(core)
    canonical_core = canonical_json(core)

    receipt_digest = canonical_receipt_hash(receipt)
    receipt_hash = bytes32_from_hex(receipt_digest, "receipt_hash")

    lineage_hash = hash_canonical({"lineage_id": lineage_id})
    subject_hash = hash_canonical(receipt["subject"])
    source_ref_hash = hash_canonical(
        {"authority_chain": authority_chain, "official_ref": official_ref}
    )

    fields = {
        "receipt_hash": receipt_hash,
        "lineage_hash": lineage_hash,
        "previous_receipt_hash": bytes32_from_hex(
            previous_receipt_hash, "previous_receipt_hash"
        ),
        "subject_hash": subject_hash,
        "source_ref_hash": source_ref_hash,
        "created_at": created_at,
        "evidence_state": evidence_state,
        "retrieval_state": retrieval_state,
    }

    return {
        "bridge_version": "receiptos.eas1797.v0.1",
        "network": "base",
        "chain_id": CHAIN_ID,
        "schema_number": EAS_SCHEMA_NUMBER,
        "schema_uid": EAS_SCHEMA_UID,
        "offline_only": True,
        "authority_created": False,
        "canonical_receipt_core": canonical_core,
        "receipt_core_sha256": receipt_hash,
        "verified_artifacts": verified_artifacts,
        "fields": fields,
    }


def write_json(path: pathlib.Path, value: Dict[str, Any]) -> None:
    reject_floats(value)
    rendered = canonical_json(value) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build offline Base EAS schema #1797 payload")
    parser.add_argument("--receipt", required=True, type=pathlib.Path)
    parser.add_argument("--lineage-id", required=True)
    parser.add_argument("--previous-receipt-hash", default=ZERO_BYTES32)
    parser.add_argument("--authority-chain", required=True)
    parser.add_argument("--official-ref", required=True)
    parser.add_argument("--created-at", required=True, type=int)
    parser.add_argument("--evidence-state", required=True)
    parser.add_argument("--retrieval-state", required=True)
    parser.add_argument(
        "--artifact",
        nargs=2,
        action="append",
        default=[],
        metavar=("PATH", "EXPECTED_SHA256"),
        help="Repeatable sealed artifact path + expected SHA-256",
    )
    parser.add_argument("--out", required=True, type=pathlib.Path)
    args = parser.parse_args()

    receipt = load_receipt(args.receipt)
    verified = verify_artifacts(args.artifact)
    payload = build_payload(
        receipt,
        lineage_id=args.lineage_id,
        previous_receipt_hash=args.previous_receipt_hash,
        authority_chain=args.authority_chain,
        official_ref=args.official_ref,
        created_at=args.created_at,
        evidence_state=parse_state(args.evidence_state, EVIDENCE_STATE, "evidence_state"),
        retrieval_state=parse_state(
            args.retrieval_state, RETRIEVAL_STATE, "retrieval_state"
        ),
        verified_artifacts=verified,
    )
    write_json(args.out, payload)

    payload_hash = sha256_bytes(args.out.read_bytes())
    print(f"EAS1797_STATUS=READY_OFFLINE")
    print(f"EAS1797_SCHEMA_UID={EAS_SCHEMA_UID}")
    print(f"EAS1797_RECEIPT_HASH={payload['fields']['receipt_hash']}")
    print(f"EAS1797_LINEAGE_HASH={payload['fields']['lineage_hash']}")
    print(f"EAS1797_SUBJECT_HASH={payload['fields']['subject_hash']}")
    print(f"EAS1797_SOURCE_REF_HASH={payload['fields']['source_ref_hash']}")
    print(f"EAS1797_PAYLOAD_SHA256={payload_hash}")
    print(f"EAS1797_PAYLOAD={args.out}")
    print("ONCHAIN_SUBMISSION=FALSE")
    print("AUTHORITY_CREATED=FALSE")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BridgeError as exc:
        print("EAS1797_STATUS=FAIL_CLOSED")
        print(f"ERROR={exc}")
        raise SystemExit(1)
