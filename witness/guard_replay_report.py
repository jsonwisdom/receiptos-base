#!/usr/bin/env python3
"""Serialization Delta Guard for Witness replay reports.

The guard treats Witness replay reports as immutable representation artifacts.
It computes a deterministic SHA-256 over canonical JSON and compares it to
an expected manifest value. It does not interpret claims, mutate state,
validate domain semantics, or promote authority/truth.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def canonical_json_bytes(value: Any) -> bytes:
    """Return deterministic UTF-8 JSON bytes for report hashing."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_hash(value: str) -> str:
    return value.strip().removeprefix("sha256:")


def read_expected_hash(expect_file: Path | None, expect_hash: str | None) -> str | None:
    if expect_hash:
        return normalize_hash(expect_hash)
    if expect_file:
        raw = expect_file.read_text(encoding="utf-8").strip()
        if raw.startswith("{"):
            manifest = json.loads(raw)
            value = manifest.get("hash")
            if not isinstance(value, str):
                raise ValueError("json_manifest_missing_hash")
            return normalize_hash(value)
        return normalize_hash(raw)
    return None


def guard_report(report: dict[str, Any], expected_hash: str | None) -> dict[str, Any]:
    computed_hash = sha256_hex(canonical_json_bytes(report))
    hash_match = expected_hash is not None and computed_hash == expected_hash

    sticky_errors: list[str] = []
    for key in ("authority", "truth_claim", "inference_performed", "state_mutated"):
        if report.get(key) is not False:
            sticky_errors.append(f"sticky_false_violation:{key}")

    consumer_safe = bool(hash_match and not sticky_errors)

    return {
        "serialization_guard": True,
        "report_loaded": True,
        "computed_hash": "sha256:" + computed_hash,
        "expected_hash": "sha256:" + expected_hash if expected_hash else None,
        "hash_match": hash_match,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "consumer_safe": consumer_safe,
        "errors": sticky_errors if expected_hash else ["missing_expected_hash", *sticky_errors],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Guard Witness replay report serialization fidelity.")
    parser.add_argument("report", type=Path)
    parser.add_argument("--expect-file", type=Path)
    parser.add_argument("--expect-hash")
    args = parser.parse_args()

    if args.expect_file and args.expect_hash:
        parser.error("use either --expect-file or --expect-hash, not both")

    report = json.loads(args.report.read_text(encoding="utf-8"))
    expected_hash = read_expected_hash(args.expect_file, args.expect_hash)
    result = guard_report(report, expected_hash)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["consumer_safe"] else 1


if __name__ == "__main__":
    sys.exit(main())
