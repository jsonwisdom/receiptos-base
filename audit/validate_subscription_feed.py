#!/usr/bin/env python3
"""Validate a root subscription feed fixture.

Checks feed shape, storage sequence continuity, root/hash shape,
allowed fields, optional storage-time anchor shape, and sticky false fields.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ALLOWED_TOP = {
    "root_subscription_manifest",
    "read_only",
    "verifier_gated",
    "subscription_ready",
    "feed_type",
    "sequence_semantics",
    "subscriber_count",
    "entries",
    "authority",
    "truth_claim",
    "inference_performed",
    "state_mutated",
    "errors",
}

ALLOWED_ENTRY = {
    "entry_id",
    "entry_sequence",
    "sequence_semantics",
    "batch_root",
    "manifest_path",
    "manifest_hash",
    "leaf_count",
    "proof_surface",
    "storage_time_anchor",
    "authority",
    "truth_claim",
    "inference_performed",
    "state_mutated",
}

STICKY_FALSE = ("authority", "truth_claim", "inference_performed", "state_mutated")


def is_sha256_uri(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("sha256:") and len(value) == 71


def validate_storage_anchor(anchor: Any, index: int) -> list[str]:
    if anchor is None:
        return []
    errors: list[str] = []
    if not isinstance(anchor, dict):
        return [f"storage_anchor_not_object:{index}"]
    allowed = {"anchor_type", "timestamp_utc", "semantics"}
    extra = sorted(set(anchor.keys()) - allowed)
    if extra:
        errors.append(f"storage_anchor_extra_fields:{index}:" + ",".join(extra))
    if anchor.get("anchor_type") != "storage_time_only":
        errors.append(f"storage_anchor_type_invalid:{index}")
    if anchor.get("semantics") != "log_storage_time_only":
        errors.append(f"storage_anchor_semantics_invalid:{index}")
    ts = anchor.get("timestamp_utc")
    if not isinstance(ts, str) or "T" not in ts or not ts.endswith("Z"):
        errors.append(f"storage_anchor_timestamp_invalid:{index}")
    return errors


def validate_feed(feed: dict[str, Any], source: str) -> dict[str, Any]:
    errors: list[str] = []

    extra_top = sorted(set(feed.keys()) - ALLOWED_TOP)
    if extra_top:
        errors.append("unauthorized_top_fields:" + ",".join(extra_top))

    required_true = ("root_subscription_manifest", "read_only", "verifier_gated", "subscription_ready")
    for key in required_true:
        if feed.get(key) is not True:
            errors.append(f"required_true_failed:{key}")

    if feed.get("feed_type") != "verified_batch_roots":
        errors.append("feed_type_invalid")
    if feed.get("sequence_semantics") != "storage_order_only":
        errors.append("sequence_semantics_invalid")

    for key in STICKY_FALSE:
        if feed.get(key) is not False:
            errors.append(f"sticky_false_failed:top:{key}")

    entries = feed.get("entries")
    if not isinstance(entries, list):
        errors.append("entries_not_list")
        entries = []

    if feed.get("subscriber_count") != len(entries):
        errors.append("subscriber_count_mismatch")

    seen_roots: set[str] = set()
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            errors.append(f"entry_not_object:{index}")
            continue

        extra_entry = sorted(set(entry.keys()) - ALLOWED_ENTRY)
        if extra_entry:
            errors.append(f"unauthorized_entry_fields:{index}:" + ",".join(extra_entry))

        if entry.get("entry_sequence") != index:
            errors.append(f"entry_sequence_mismatch:{index}")
        if entry.get("sequence_semantics") != "storage_order_only":
            errors.append(f"entry_sequence_semantics_invalid:{index}")

        batch_root = entry.get("batch_root")
        manifest_hash = entry.get("manifest_hash")
        if not is_sha256_uri(batch_root):
            errors.append(f"batch_root_invalid:{index}")
        elif batch_root in seen_roots:
            errors.append(f"duplicate_batch_root:{index}")
        else:
            seen_roots.add(batch_root)
        if not is_sha256_uri(manifest_hash):
            errors.append(f"manifest_hash_invalid:{index}")

        if entry.get("proof_surface") != "manifest_path":
            errors.append(f"proof_surface_invalid:{index}")

        if "storage_time_anchor" in entry:
            errors.extend(validate_storage_anchor(entry.get("storage_time_anchor"), index))

        for key in STICKY_FALSE:
            if entry.get(key) is not False:
                errors.append(f"sticky_false_failed:{index}:{key}")

    valid = not errors
    return {
        "subscription_feed_validator": True,
        "source": source,
        "feed_valid": valid,
        "entry_count": len(entries),
        "sequence_continuity_valid": valid,
        "root_hashes_valid": valid,
        "manifest_hashes_valid": valid,
        "unauthorized_fields_valid": valid,
        "storage_time_anchors_valid": valid,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a root subscription feed fixture.")
    parser.add_argument("feed", type=Path)
    args = parser.parse_args()

    feed = json.loads(args.feed.read_text(encoding="utf-8"))
    result = validate_feed(feed, str(args.feed))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["feed_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
