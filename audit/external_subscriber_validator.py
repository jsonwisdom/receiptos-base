#!/usr/bin/env python3
"""External subscriber validator for storage-view subscription feed v0.

Validates that a subscriber contract consumes the feed without adding event-time,
causation, priority, authority, truth, inference, or write behavior.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
if str(AUDIT) not in sys.path:
    sys.path.insert(0, str(AUDIT))

from validate_storage_view_subscription import validate_feed as validate_subscription_feed  # noqa: E402
from storage_view_subscription_feed import build_feed  # noqa: E402

ALLOWED_SUBSCRIBER_FIELDS = {
    "subscriber_contract_v0",
    "read_only",
    "allowed_methods",
    "cursor_field",
    "allowed_ordering",
    "forbidden_semantics",
    "preserve_sticky_fields",
    "authority",
    "truth_claim",
    "inference_performed",
    "state_mutated",
}

FORBIDDEN_TERMS = (
    "event_time",
    "event_order",
    "causation",
    "causal",
    "priority",
    "evidentiary_strength",
    "truth_progression",
    "authority_true",
)

STICKY_FALSE = ("authority", "truth_claim", "inference_performed", "state_mutated")


def validate_subscriber_contract(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    extra = sorted(set(contract.keys()) - ALLOWED_SUBSCRIBER_FIELDS)
    if extra:
        errors.append("subscriber_unauthorized_fields:" + ",".join(extra))

    if contract.get("subscriber_contract_v0") is not True:
        errors.append("subscriber_contract_marker_missing")
    if contract.get("read_only") is not True:
        errors.append("subscriber_not_read_only")

    methods = contract.get("allowed_methods")
    if methods != ["GET"]:
        errors.append("subscriber_write_method_allowed")

    if contract.get("cursor_field") != "storage_timestamp_utc":
        errors.append("subscriber_cursor_invalid")
    if contract.get("allowed_ordering") != "storage_time_only":
        errors.append("subscriber_ordering_invalid")

    forbidden = contract.get("forbidden_semantics")
    if not isinstance(forbidden, list):
        errors.append("subscriber_forbidden_semantics_missing")
        forbidden = []
    for term in FORBIDDEN_TERMS:
        if term not in forbidden:
            errors.append(f"subscriber_forbidden_semantic_missing:{term}")

    if contract.get("preserve_sticky_fields") is not True:
        errors.append("subscriber_sticky_preservation_missing")
    for key in STICKY_FALSE:
        if contract.get(key) is not False:
            errors.append(f"subscriber_sticky_false_failed:{key}")

    return errors


def validate_external_subscriber(feed_path: Path, contract_path: Path, repo_root: Path) -> dict[str, Any]:
    feed = build_feed(feed_path, repo_root)
    feed_check = validate_subscription_feed(feed)
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    contract_errors = validate_subscriber_contract(contract)

    errors: list[str] = []
    if feed_check.get("feed_valid") is not True:
        errors.extend(["feed_invalid", *feed_check.get("errors", [])])
    errors.extend(contract_errors)

    passed = not errors
    return {
        "external_subscriber_validator": True,
        "subscriber_valid": passed,
        "feed_valid": feed_check.get("feed_valid") is True,
        "contract_valid": not contract_errors,
        "read_only_valid": "subscriber_write_method_allowed" not in contract_errors and "subscriber_not_read_only" not in contract_errors,
        "cursor_valid": "subscriber_cursor_invalid" not in contract_errors,
        "ordering_valid": "subscriber_ordering_invalid" not in contract_errors,
        "forbidden_semantics_valid": not any(error.startswith("subscriber_forbidden_semantic_missing") for error in contract_errors),
        "sticky_fields_valid": not any("sticky" in error for error in contract_errors),
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an external subscriber contract for the storage-view feed.")
    parser.add_argument("feed", type=Path)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    result = validate_external_subscriber(args.feed, args.contract, args.repo_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["subscriber_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
