#!/usr/bin/env python3
"""Validate FREE_ONLY_THREE_SURFACE_RECEIPT_V0_2 receipts.

This verifier is intentionally narrow:
- validates boundary fields
- validates all three required surfaces are observed
- rejects trace/internal-call, wallet-control, creator-identity, authenticity,
  payment/sale, and legal-ownership elevation
- skips other receipt types by default so legacy receipt families are not
  mutated into fake three-surface receipts
- does not call RPC
- does not prove ownership, identity, authenticity, payment, sale, or legal truth
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RECEIPT_TYPE = "FREE_ONLY_THREE_SURFACE_RECEIPT_V0_2"

REQUIRED_FALSE = {
    ("authority",): False,
    ("trace", "internal_calls_observed"): False,
    ("boundary", "proves_internal_trace"): False,
    ("boundary", "proves_wallet_control"): False,
    ("boundary", "proves_creator_identity"): False,
    ("boundary", "proves_token_authenticity"): False,
    ("boundary", "proves_payment_or_sale"): False,
}

OPTIONAL_FALSE = {
    ("boundary", "proves_legal_ownership"): False,
}

REQUIRED_TRUE = {
    ("free_only",): True,
    ("no_fake_green",): True,
}

REQUIRED_OBSERVED_SURFACES = {
    ("surfaces", "tx_receipt"): "observed",
    ("surfaces", "log_surface"): "observed",
    ("surfaces", "state_read"): "observed",
}

REQUIRED_TRACE_VALUES = {
    ("trace", "debug_traceTransaction"): "not_used",
}

FORBIDDEN_STRINGS = [
    "wallet control proved",
    "creator identity proved",
    "token authenticity proved",
    "payment proved",
    "sale proved",
    "legal ownership proved",
    "trace observed",
    "internal calls observed",
]


def get_path(data: dict[str, Any], path: tuple[str, ...]) -> Any:
    cur: Any = data
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            raise KeyError(".".join(path))
        cur = cur[key]
    return cur


def iter_json_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.rglob("*.json"))


def validate_receipt(data: dict[str, Any], file_path: Path) -> list[str]:
    errors: list[str] = []

    if data.get("receipt_type") != RECEIPT_TYPE:
        errors.append(
            f"{file_path}: receipt_type must be {RECEIPT_TYPE!r} for this verifier"
        )

    for path, expected in REQUIRED_FALSE.items():
        try:
            actual = get_path(data, path)
        except KeyError:
            errors.append(f"{file_path}: missing required field {'.'.join(path)}")
            continue
        if actual is not expected:
            errors.append(f"{file_path}: {'.'.join(path)} must be {expected!r}, got {actual!r}")

    for path, expected in OPTIONAL_FALSE.items():
        try:
            actual = get_path(data, path)
        except KeyError:
            continue
        if actual is not expected:
            errors.append(f"{file_path}: {'.'.join(path)} must be {expected!r}, got {actual!r}")

    for path, expected in REQUIRED_TRUE.items():
        try:
            actual = get_path(data, path)
        except KeyError:
            errors.append(f"{file_path}: missing required field {'.'.join(path)}")
            continue
        if actual is not expected:
            errors.append(f"{file_path}: {'.'.join(path)} must be {expected!r}, got {actual!r}")

    for path, expected in REQUIRED_OBSERVED_SURFACES.items():
        try:
            actual = get_path(data, path)
        except KeyError:
            errors.append(f"{file_path}: missing required surface {'.'.join(path)}")
            continue
        if actual != expected:
            errors.append(f"{file_path}: {'.'.join(path)} must be {expected!r}, got {actual!r}")

    for path, expected in REQUIRED_TRACE_VALUES.items():
        try:
            actual = get_path(data, path)
        except KeyError:
            errors.append(f"{file_path}: missing required field {'.'.join(path)}")
            continue
        if actual != expected:
            errors.append(f"{file_path}: {'.'.join(path)} must be {expected!r}, got {actual!r}")

    haystack = json.dumps(data, sort_keys=True).lower()
    for phrase in FORBIDDEN_STRINGS:
        if phrase in haystack:
            errors.append(f"{file_path}: forbidden claim phrase present: {phrase!r}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate free-only three-surface receipts")
    parser.add_argument("paths", nargs="+", help="Receipt JSON files or directories to validate")
    parser.add_argument(
        "--strict-type",
        action="store_true",
        help="Fail when a JSON receipt has a different receipt_type. Default is to skip out-of-scope receipt families.",
    )
    args = parser.parse_args()

    errors: list[str] = []
    checked = 0
    skipped = 0

    for raw_path in args.paths:
        path = Path(raw_path)
        if not path.exists():
            errors.append(f"{path}: path does not exist")
            continue
        for file_path in iter_json_files(path):
            try:
                data = json.loads(file_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"{file_path}: invalid JSON: {exc}")
                continue
            if not isinstance(data, dict):
                errors.append(f"{file_path}: top-level JSON must be an object")
                continue

            if data.get("receipt_type") != RECEIPT_TYPE:
                if args.strict_type:
                    errors.append(
                        f"{file_path}: receipt_type must be {RECEIPT_TYPE!r} for this verifier"
                    )
                else:
                    skipped += 1
                continue

            checked += 1
            errors.extend(validate_receipt(data, file_path))

    if errors:
        print("FREE_ONLY_THREE_SURFACE_RECEIPT_V0_2 validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "FREE_ONLY_THREE_SURFACE_RECEIPT_V0_2 validation passed: "
        f"{checked} checked, {skipped} skipped out-of-scope"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
