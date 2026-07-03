#!/usr/bin/env python3
"""Build deterministic EAS payloads from ReplayBoard settlement ledgers.

This script is offline-only. It does not sign, submit, mutate, or fetch chain state.
It reads the settlement JSONL tip, verifies the receipt hash boundary, and emits a
canonical JSON payload suitable for the ReceiptOSReplayRailV1 EAS schema.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from typing import Any, Dict, List, Optional

PAYLOAD_SCHEMA_VERSION = "receiptos.eas_payload.v0.1"
EAS_SCHEMA_NAME = "ReceiptOSReplayRailV1"
VERIFIER_VERSION = "REPLAYBOARD_EAS_PAYLOAD_V1"
DEFAULT_CHAIN_ID = 8453
DEFAULT_SOURCE_REPO = "jsonwisdom/receiptos-base"
DEFAULT_SOURCE_REF = "replay-gate-v1"
REQUIRED_INVARIANTS = {
    "authority": False,
    "fail_closed": True,
    "replayable": True,
    "truth_claim": False,
    "witness_only": True,
}


class PayloadError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def normalize(value: Any) -> Any:
    if value is None or isinstance(value, bool) or isinstance(value, int):
        return value
    if isinstance(value, float):
        raise PayloadError("CANONICALIZATION_FAILURE floats_not_allowed")
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if isinstance(value, dict):
        return {str(key).strip(): normalize(value[key]) for key in sorted(value)}
    raise PayloadError(f"CANONICALIZATION_FAILURE unsupported_type={type(value).__name__}")


def canonical_json(value: Any) -> str:
    return json.dumps(normalize(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def receipt_hash(receipt: Dict[str, Any]) -> str:
    basis = dict(receipt)
    basis["receipt_hash"] = None
    return sha256_bytes(canonical_json(basis).encode("utf-8"))


def load_jsonl(path: pathlib.Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise PayloadError(f"INVALID_JSONL line={line_number} error={exc}") from exc
            if not isinstance(row, dict):
                raise PayloadError(f"RECEIPT_MUST_BE_OBJECT line={line_number}")
            rows.append(row)
    if not rows:
        raise PayloadError("EMPTY_LEDGER")
    return rows


def require_sha256(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:") or len(value) != 71:
        raise PayloadError(f"INVALID_SHA256_FIELD field={field} value={value}")
    return value


def verify_tip_receipt(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    tip = rows[-1]

    recorded = require_sha256(tip.get("receipt_hash"), "receipt_hash")
    recomputed = receipt_hash(tip)
    if recorded != recomputed:
        raise PayloadError(f"TIP_RECEIPT_HASH_MISMATCH expected={recorded} actual={recomputed}")

    require_sha256(tip.get("prev_receipt_hash"), "prev_receipt_hash")

    invariants = tip.get("invariants")
    if invariants != REQUIRED_INVARIANTS:
        raise PayloadError(f"INVARIANT_MISMATCH actual={invariants}")

    evidence = tip.get("evidence")
    if not isinstance(evidence, dict):
        raise PayloadError("EVIDENCE_MISSING")
    if evidence.get("hash_method") != "sha256(raw_response_body_bytes)":
        raise PayloadError("HASH_METHOD_MISMATCH")

    content_hash = evidence.get("content_hash")
    if content_hash is not None:
        require_sha256(content_hash, "evidence.content_hash")

    return tip


def maybe_verify_raw_evidence(tip: Dict[str, Any], raw_evidence: Optional[pathlib.Path]) -> None:
    if not raw_evidence:
        return
    evidence = tip.get("evidence")
    if not isinstance(evidence, dict):
        raise PayloadError("EVIDENCE_MISSING")
    expected = evidence.get("content_hash")
    actual = sha256_bytes(raw_evidence.read_bytes())
    if expected != actual:
        raise PayloadError(f"EVIDENCE_HASH_MISMATCH expected={expected} actual={actual}")


def build_payload(
    tip: Dict[str, Any],
    *,
    ledger_path: pathlib.Path,
    chain_id: int,
    source_repo: str,
    source_ref: str,
    schema_uid: Optional[str],
) -> Dict[str, Any]:
    evidence = tip.get("evidence")
    if not isinstance(evidence, dict):
        raise PayloadError("EVIDENCE_MISSING")

    payload: Dict[str, Any] = {
        "schema_version": PAYLOAD_SCHEMA_VERSION,
        "eas_schema_name": EAS_SCHEMA_NAME,
        "eas_schema_uid": schema_uid,
        "receipt_hash": require_sha256(tip.get("receipt_hash"), "receipt_hash"),
        "prev_receipt_hash": require_sha256(tip.get("prev_receipt_hash"), "prev_receipt_hash"),
        "ledger_tip_hash": require_sha256(tip.get("receipt_hash"), "ledger_tip_hash"),
        "claim_id": tip.get("claim_id"),
        "status": tip.get("status"),
        "resolution": tip.get("resolution"),
        "reason": tip.get("reason"),
        "canonicalizer_version": tip.get("canonicalizer_version"),
        "verifier_version": VERIFIER_VERSION,
        "source_repo": source_repo,
        "source_ref": source_ref,
        "chain_id": chain_id,
        "authority": False,
        "truth_claim": False,
        "witness_only": True,
        "evidence_summary": {
            "content_hash": evidence.get("content_hash"),
            "body_size_bytes": evidence.get("body_size_bytes"),
            "hash_method": evidence.get("hash_method"),
            "requested_url": evidence.get("requested_url"),
            "final_url": evidence.get("final_url"),
            "status_code": evidence.get("status_code"),
            "error": evidence.get("error"),
        },
        "ledger": {
            "path_hint": str(ledger_path),
            "line_count": None,
        },
    }

    if not isinstance(payload["claim_id"], str) or not payload["claim_id"]:
        raise PayloadError("CLAIM_ID_MISSING")
    if not isinstance(payload["canonicalizer_version"], str) or not payload["canonicalizer_version"]:
        raise PayloadError("CANONICALIZER_VERSION_MISSING")
    if not isinstance(payload["status"], str) or not payload["status"]:
        raise PayloadError("STATUS_MISSING")

    return payload


def write_payload(path: Optional[pathlib.Path], payload: Dict[str, Any]) -> None:
    rendered = canonical_json(payload) + "\n"
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build canonical EAS payload from ReplayBoard settle ledger")
    parser.add_argument("--ledger", required=True, type=pathlib.Path)
    parser.add_argument("--raw-evidence", type=pathlib.Path)
    parser.add_argument("--out", type=pathlib.Path)
    parser.add_argument("--chain-id", default=DEFAULT_CHAIN_ID, type=int)
    parser.add_argument("--source-repo", default=DEFAULT_SOURCE_REPO)
    parser.add_argument("--source-ref", default=DEFAULT_SOURCE_REF)
    parser.add_argument("--schema-uid")
    args = parser.parse_args()

    rows = load_jsonl(args.ledger)
    tip = verify_tip_receipt(rows)
    maybe_verify_raw_evidence(tip, args.raw_evidence)
    payload = build_payload(
        tip,
        ledger_path=args.ledger,
        chain_id=args.chain_id,
        source_repo=args.source_repo,
        source_ref=args.source_ref,
        schema_uid=args.schema_uid,
    )
    payload["ledger"]["line_count"] = len(rows)
    write_payload(args.out, payload)

    if args.out:
        print(f"RECEIPTOS_EAS_PAYLOAD={args.out}")
    print(f"RECEIPTOS_EAS_PAYLOAD_HASH={sha256_bytes(canonical_json(payload).encode('utf-8'))}")
    print(f"RECEIPTOS_RECEIPT_HASH={payload['receipt_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
