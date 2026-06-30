#!/usr/bin/env python3
"""Hash-only catalog for accepted lattice ingestion artifacts.

Pattern: flat map keyed by source_report_hash.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

STICKY_FALSE = ("authority", "truth_claim", "inference_performed", "state_mutated")


def build_catalog_entry(artifact: dict[str, Any], source: str) -> dict[str, Any]:
    errors: list[str] = []

    required_true = {
        "lattice_ingestion": artifact.get("lattice_ingestion"),
        "ingestion_accepted": artifact.get("ingestion_accepted"),
        "guard_consumer_safe": artifact.get("guard_consumer_safe"),
        "guard_hash_match": artifact.get("guard_hash_match"),
    }
    for key, value in required_true.items():
        if value is not True:
            errors.append(f"required_true_failed:{key}")

    for key in STICKY_FALSE:
        if artifact.get(key) is not False:
            errors.append(f"sticky_false_failed:{key}")

    source_report_hash = artifact.get("source_report_hash")
    if not isinstance(source_report_hash, str) or not source_report_hash.startswith("sha256:"):
        errors.append("source_report_hash_invalid")

    accepted = not errors
    entries: dict[str, Any] = {}
    if accepted:
        entries[source_report_hash] = {
            "source_artifact": source,
            "source_report": artifact.get("source_report"),
            "guard_consumer_safe": True,
            "guard_hash_match": True,
            "authority": False,
            "truth_claim": False,
            "inference_performed": False,
            "state_mutated": False,
        }

    return {
        "lattice_catalog": True,
        "catalog_type": "flat_hash_map",
        "accepted_for_catalog": accepted,
        "indexed_count": len(entries),
        "entries": entries,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Catalog an accepted lattice ingestion artifact by hash.")
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()

    artifact = json.loads(args.artifact.read_text(encoding="utf-8"))
    result = build_catalog_entry(artifact, str(args.artifact))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["accepted_for_catalog"] else 1


if __name__ == "__main__":
    sys.exit(main())
