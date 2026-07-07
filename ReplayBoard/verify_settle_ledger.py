#!/usr/bin/env python3
"""Deterministic ReplayBoard settlement ledger verifier.

Verifies the receipt chain without re-fetching external evidence:
- ledger is valid JSONL
- every receipt hash recomputes canonically
- prev_receipt_hash links exactly
- witness invariants remain locked
- optional raw evidence bytes match the final receipt evidence.content_hash
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from typing import Any, Dict, List, Optional

GENESIS_PREV_RECEIPT_HASH = "sha256:" + "0" * 64
REQUIRED_INVARIANTS = {
    "authority": False,
    "fail_closed": True,
    "replayable": True,
    "truth_claim": False,
    "witness_only": True,
}


class VerifyError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def normalize(value: Any) -> Any:
    if value is None or isinstance(value, bool) or isinstance(value, int):
        return value
    if isinstance(value, float):
        raise VerifyError("CANONICALIZATION_FAILURE floats_not_allowed")
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if isinstance(value, dict):
        return {str(key).strip(): normalize(value[key]) for key in sorted(value)}
    raise VerifyError(f"CANONICALIZATION_FAILURE unsupported_type={type(value).__name__}")


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
                raise VerifyError(f"INVALID_JSONL line={line_number} error={exc}") from exc
            if not isinstance(row, dict):
                raise VerifyError(f"RECEIPT_MUST_BE_OBJECT line={line_number}")
            rows.append(row)
    if not rows:
        raise VerifyError("EMPTY_LEDGER")
    return rows


def verify_rows(rows: List[Dict[str, Any]]) -> str:
    expected_prev = GENESIS_PREV_RECEIPT_HASH
    final_hash: Optional[str] = None

    for index, row in enumerate(rows, start=1):
        actual_prev = row.get("prev_receipt_hash")
        if actual_prev != expected_prev:
            raise VerifyError(
                f"CHAIN_LINK_MISMATCH line={index} expected_prev={expected_prev} actual_prev={actual_prev}"
            )

        recorded_hash = row.get("receipt_hash")
        if not isinstance(recorded_hash, str) or not recorded_hash.startswith("sha256:"):
            raise VerifyError(f"INVALID_RECEIPT_HASH line={index}")

        recomputed_hash = receipt_hash(row)
        if recomputed_hash != recorded_hash:
            raise VerifyError(
                f"RECEIPT_HASH_MISMATCH line={index} expected={recorded_hash} actual={recomputed_hash}"
            )

        invariants = row.get("invariants")
        if invariants != REQUIRED_INVARIANTS:
            raise VerifyError(f"INVARIANT_MISMATCH line={index} actual={invariants}")

        evidence = row.get("evidence")
        if not isinstance(evidence, dict):
            raise VerifyError(f"EVIDENCE_MISSING line={index}")
        if evidence.get("hash_method") != "sha256(raw_response_body_bytes)":
            raise VerifyError(f"HASH_METHOD_MISMATCH line={index}")

        expected_prev = recorded_hash
        final_hash = recorded_hash

    assert final_hash is not None
    return final_hash


def verify_raw_evidence(rows: List[Dict[str, Any]], raw_evidence: pathlib.Path) -> None:
    final_receipt = rows[-1]
    evidence = final_receipt.get("evidence")
    if not isinstance(evidence, dict):
        raise VerifyError("FINAL_EVIDENCE_MISSING")
    expected = evidence.get("content_hash")
    actual = sha256_bytes(raw_evidence.read_bytes())
    if expected != actual:
        raise VerifyError(f"EVIDENCE_HASH_MISMATCH expected={expected} actual={actual}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify ReplayBoard settlement JSONL ledger")
    parser.add_argument("--ledger", required=True, type=pathlib.Path)
    parser.add_argument("--raw-evidence", type=pathlib.Path)
    args = parser.parse_args()

    rows = load_jsonl(args.ledger)
    final_hash = verify_rows(rows)
    if args.raw_evidence:
        verify_raw_evidence(rows, args.raw_evidence)

    print("REPLAYBOARD_REPLAY_GATE=PASS")
    print(f"REPLAYBOARD_RECEIPTS_VERIFIED={len(rows)}")
    print(f"REPLAYBOARD_FINAL_RECEIPT_HASH={final_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
