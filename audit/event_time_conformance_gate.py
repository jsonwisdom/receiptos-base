#!/usr/bin/env python3
"""Event-time boundary conformance gate.

Validates proposed event-time work before any parser or extractor exists.
The gate enforces separation from the closed storage-time stack.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

STICKY_FALSE = ("authority", "truth_claim", "inference_performed", "state_mutated")

CLOSED_STORAGE_PATHS = (
    "audit/storage_time_view.py",
    "audit/storage_view_subscription_feed.py",
    "audit/validate_storage_view_subscription.py",
    "audit/conformance_gate_storage_view.py",
    "audit/export_storage_time_view.py",
    "docs/TIMELINE_SEMANTICS_V0_STORAGE_VIEW.md",
    "docs/STORAGE_VIEW_SUBSCRIPTION_FEED_V0.md",
)

FORBIDDEN_IMPORT_FRAGMENTS = (
    "storage_time_view",
    "storage_view_subscription_feed",
    "validate_storage_view_subscription",
    "conformance_gate_storage_view",
    "export_storage_time_view",
)

ALLOWED_TOP = {
    "event_time_boundary_proposal",
    "proposal_id",
    "issue",
    "touched_files",
    "imports",
    "event_time_source",
    "event_time_path",
    "authority",
    "truth_claim",
    "inference_performed",
    "state_mutated",
}


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    extra = sorted(set(manifest.keys()) - ALLOWED_TOP)
    if extra:
        errors.append("unauthorized_top_fields:" + ",".join(extra))

    if manifest.get("event_time_boundary_proposal") is not True:
        errors.append("proposal_marker_missing")
    if manifest.get("issue") != "#42":
        errors.append("issue_reference_invalid")
    if manifest.get("event_time_source") != "external":
        errors.append("event_time_source_invalid")

    event_time_path = manifest.get("event_time_path")
    if not isinstance(event_time_path, str) or not (event_time_path.startswith("event_time/") or event_time_path.startswith("semantics/event_time/")):
        errors.append("event_time_path_invalid")

    touched_files = manifest.get("touched_files")
    if not isinstance(touched_files, list):
        errors.append("touched_files_not_list")
        touched_files = []
    for item in touched_files:
        if item in CLOSED_STORAGE_PATHS:
            errors.append("closed_storage_file_touched:" + item)

    imports = manifest.get("imports")
    if not isinstance(imports, list):
        errors.append("imports_not_list")
        imports = []
    for item in imports:
        if not isinstance(item, str):
            errors.append("import_not_string")
            continue
        for fragment in FORBIDDEN_IMPORT_FRAGMENTS:
            if fragment in item:
                errors.append("forbidden_storage_import:" + item)

    for key in STICKY_FALSE:
        if manifest.get(key) is not False:
            errors.append("sticky_false_failed:" + key)

    passed = not errors
    return {
        "event_time_conformance_gate": True,
        "gate_passed": passed,
        "closed_storage_paths_untouched": not any(error.startswith("closed_storage_file_touched") for error in errors),
        "storage_imports_absent": not any(error.startswith("forbidden_storage_import") for error in errors),
        "event_time_source_valid": "event_time_source_invalid" not in errors,
        "event_time_path_valid": "event_time_path_invalid" not in errors,
        "sticky_fields_valid": not any(error.startswith("sticky_false_failed") for error in errors),
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate event-time boundary proposal.")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = validate_manifest(manifest)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["gate_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
