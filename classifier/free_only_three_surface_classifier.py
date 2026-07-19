#!/usr/bin/env python3
"""Classify receipts for ALMS routing without adding authority.

The classifier is a routing layer, not a truth engine.
It answers:
- should this artifact enter ALMS memory?
- under what witness-only scope?
- if not, why not?

It does not call RPC, mutate receipts, prove ownership, prove identity,
prove authenticity, prove payment, prove sale, or prove legal truth.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RECEIPT_TYPE = "FREE_ONLY_THREE_SURFACE_RECEIPT_V0_2"
CLASSIFICATION_TYPE = "RECEIPT_CLASSIFICATION_V0_1"

CLAIM_SCOPE = [
    "tx_receipt_observed",
    "logs_observed",
    "state_read_observed",
]

FORBIDDEN_SCOPE = [
    "wallet_control",
    "creator_identity",
    "token_authenticity",
    "payment_or_sale",
    "legal_ownership",
    "trace_internal_calls",
]


def get_path(data: dict[str, Any], path: tuple[str, ...]) -> Any:
    cur: Any = data
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            raise KeyError(".".join(path))
        cur = cur[key]
    return cur


def classify(data: dict[str, Any]) -> dict[str, Any]:
    receipt_type = data.get("receipt_type")

    if receipt_type != RECEIPT_TYPE:
        return {
            "classification_type": CLASSIFICATION_TYPE,
            "source_receipt_type": receipt_type,
            "route": "LEGACY_RECEIPT_ROUTER",
            "admissibility": "OUT_OF_SCOPE",
            "surface_level": "UNKNOWN",
            "authority": False,
            "memory_safe": False,
            "claim_scope": [],
            "forbidden_scope": FORBIDDEN_SCOPE,
            "reason": "receipt type is outside FREE_ONLY_THREE_SURFACE_RECEIPT_V0_2 classifier scope",
            "errors": [],
        }

    checks = {
        "authority": (("authority",), False),
        "free_only": (("free_only",), True),
        "no_fake_green": (("no_fake_green",), True),
        "surfaces.tx_receipt": (("surfaces", "tx_receipt"), "observed"),
        "surfaces.log_surface": (("surfaces", "log_surface"), "observed"),
        "surfaces.state_read": (("surfaces", "state_read"), "observed"),
        "trace.debug_traceTransaction": (("trace", "debug_traceTransaction"), "not_used"),
        "trace.internal_calls_observed": (("trace", "internal_calls_observed"), False),
        "boundary.proves_internal_trace": (("boundary", "proves_internal_trace"), False),
        "boundary.proves_wallet_control": (("boundary", "proves_wallet_control"), False),
        "boundary.proves_creator_identity": (("boundary", "proves_creator_identity"), False),
        "boundary.proves_token_authenticity": (("boundary", "proves_token_authenticity"), False),
        "boundary.proves_payment_or_sale": (("boundary", "proves_payment_or_sale"), False),
    }

    errors: list[str] = []
    for label, (path, expected) in checks.items():
        try:
            actual = get_path(data, path)
        except KeyError:
            errors.append(f"missing required field {label}")
            continue
        if actual != expected:
            errors.append(f"{label} must be {expected!r}, got {actual!r}")

    try:
        legal_ownership = get_path(data, ("boundary", "proves_legal_ownership"))
    except KeyError:
        legal_ownership = False
    if legal_ownership is not False:
        errors.append(f"boundary.proves_legal_ownership must be False, got {legal_ownership!r}")

    if errors:
        return {
            "classification_type": CLASSIFICATION_TYPE,
            "source_receipt_type": receipt_type,
            "route": "REJECTED_INTAKE",
            "admissibility": "INVALID",
            "surface_level": "NONE",
            "authority": False,
            "memory_safe": False,
            "claim_scope": [],
            "forbidden_scope": FORBIDDEN_SCOPE,
            "reason": "receipt failed free-only three-surface admissibility checks",
            "errors": errors,
        }

    return {
        "classification_type": CLASSIFICATION_TYPE,
        "source_receipt_type": receipt_type,
        "route": "ALMS_WITNESS_LEDGER",
        "admissibility": "ADMISSIBLE_WITNESS",
        "surface_level": "THREE_SURFACE_V0_2",
        "authority": False,
        "memory_safe": True,
        "claim_scope": CLAIM_SCOPE,
        "forbidden_scope": FORBIDDEN_SCOPE,
        "reason": "receipt is admissible as witness-only ALMS memory input",
        "errors": [],
    }


def iter_json_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.rglob("*.json"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify receipts for ALMS routing")
    parser.add_argument("paths", nargs="+", help="Receipt JSON files or directories to classify")
    parser.add_argument("--jsonl", action="store_true", help="Emit JSON Lines instead of pretty JSON array")
    args = parser.parse_args()

    outputs: list[dict[str, Any]] = []

    for raw_path in args.paths:
        path = Path(raw_path)
        if not path.exists():
            outputs.append(
                {
                    "classification_type": CLASSIFICATION_TYPE,
                    "source_receipt_type": None,
                    "route": "REJECTED_INTAKE",
                    "admissibility": "INVALID",
                    "surface_level": "NONE",
                    "authority": False,
                    "memory_safe": False,
                    "claim_scope": [],
                    "forbidden_scope": FORBIDDEN_SCOPE,
                    "reason": "path does not exist",
                    "errors": [str(path)],
                }
            )
            continue

        for file_path in iter_json_files(path):
            try:
                data = json.loads(file_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                outputs.append(
                    {
                        "classification_type": CLASSIFICATION_TYPE,
                        "source_receipt_type": None,
                        "route": "REJECTED_INTAKE",
                        "admissibility": "INVALID",
                        "surface_level": "NONE",
                        "authority": False,
                        "memory_safe": False,
                        "claim_scope": [],
                        "forbidden_scope": FORBIDDEN_SCOPE,
                        "reason": "invalid JSON",
                        "errors": [f"{file_path}: {exc}"],
                    }
                )
                continue

            if not isinstance(data, dict):
                outputs.append(
                    {
                        "classification_type": CLASSIFICATION_TYPE,
                        "source_receipt_type": None,
                        "route": "REJECTED_INTAKE",
                        "admissibility": "INVALID",
                        "surface_level": "NONE",
                        "authority": False,
                        "memory_safe": False,
                        "claim_scope": [],
                        "forbidden_scope": FORBIDDEN_SCOPE,
                        "reason": "top-level JSON must be an object",
                        "errors": [str(file_path)],
                    }
                )
                continue

            result = classify(data)
            result["source_path"] = str(file_path)
            outputs.append(result)

    if args.jsonl:
        for item in outputs:
            print(json.dumps(item, sort_keys=True))
    else:
        print(json.dumps(outputs, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
