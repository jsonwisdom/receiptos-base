#!/usr/bin/env python3
"""Append-only audit logger for batch roots.

Records batch root manifests as opaque commitments.
Append sequence is storage order only.
Optional anchors record storage time only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

STICKY_FALSE = ("authority", "truth_claim", "inference_performed", "state_mutated")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_uri(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def load_entries(log_path: Path) -> list[dict[str, Any]]:
    if not log_path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entries.append(json.loads(line))
    return entries


def build_storage_anchor(timestamp_utc: str | None) -> dict[str, str] | None:
    if not timestamp_utc:
        return None
    return {
        "anchor_type": "storage_time_only",
        "timestamp_utc": timestamp_utc,
        "semantics": "log_storage_time_only",
    }


def validate_storage_anchor(anchor: dict[str, Any] | None) -> list[str]:
    if anchor is None:
        return []
    errors: list[str] = []
    if anchor.get("anchor_type") != "storage_time_only":
        errors.append("storage_anchor_type_invalid")
    if anchor.get("semantics") != "log_storage_time_only":
        errors.append("storage_anchor_semantics_invalid")
    timestamp = anchor.get("timestamp_utc")
    if not isinstance(timestamp, str) or not timestamp.endswith("Z") or "T" not in timestamp:
        errors.append("storage_anchor_timestamp_invalid")
    return errors


def build_entry(manifest: dict[str, Any], manifest_path: str, sequence: int, timestamp_utc: str | None = None) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    for key in STICKY_FALSE:
        if manifest.get(key) is not False:
            errors.append(f"manifest_sticky_false_failed:{key}")

    if manifest.get("batch_root_manifest") is not True:
        errors.append("manifest_not_batch_root_manifest")
    if manifest.get("accepted_for_manifest") is not True:
        errors.append("manifest_not_accepted")

    batch_root = manifest.get("merkle_root")
    if not isinstance(batch_root, str) or not batch_root.startswith("sha256:"):
        errors.append("batch_root_invalid")

    manifest_hash = sha256_uri(canonical_json_bytes(manifest))
    entry_id = f"batch-root-entry-{sequence:06d}"
    entry = {
        "audit_log_append": True,
        "entry_id": entry_id,
        "entry_sequence": sequence,
        "batch_root": batch_root,
        "manifest_path": manifest_path,
        "manifest_hash": manifest_hash,
        "leaf_count": manifest.get("leaf_count"),
        "source_use_case": manifest.get("manifest_use_case"),
        "append_sequence_semantics": "storage_order_only",
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
    }
    anchor = build_storage_anchor(timestamp_utc)
    errors.extend(validate_storage_anchor(anchor))
    if anchor:
        entry["storage_time_anchor"] = anchor
    return entry, errors


def append_entry(log_path: Path, manifest_path: Path, timestamp_utc: str | None = None) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = load_entries(log_path)
    sequence = len(entries) + 1
    entry, errors = build_entry(manifest, str(manifest_path), sequence, timestamp_utc)

    existing_roots = {item.get("batch_root") for item in entries}
    if entry.get("batch_root") in existing_roots:
        errors.append("duplicate_batch_root")

    append_accepted = not errors
    if append_accepted:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")

    return {
        "audit_log_append": True,
        "append_accepted": append_accepted,
        "entry": entry if append_accepted else None,
        "entry_sequence": sequence,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a batch root manifest to an audit JSONL log.")
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--storage-time-utc")
    args = parser.parse_args()

    result = append_entry(args.log, args.manifest, args.storage_time_utc)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["append_accepted"] else 1


if __name__ == "__main__":
    sys.exit(main())
