#!/usr/bin/env python3
"""Merkle catalog over a flat lattice hash catalog.

Input: a flat catalog produced by catalog_accepted_report.py.
Output: a deterministic binary Merkle root over accepted report hashes.

Rules:
- leaves are source_report_hash keys from the catalog entries
- leaves are sorted lexicographically
- a single leaf is its own root
- odd leaf count duplicates the last leaf for the next level
- branch hash = sha256(left_hex + right_hex) as UTF-8 hex text

This module adds commitment structure only. It does not add scoring,
relations, simulation, graph mutation, or authority/truth promotion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

STICKY_FALSE = ("authority", "truth_claim", "inference_performed", "state_mutated")


def normalize_hash(value: str) -> str:
    return value.removeprefix("sha256:")


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def merkle_root(leaves: list[str]) -> tuple[str | None, list[list[str]]]:
    if not leaves:
        return None, []

    level = sorted(normalize_hash(leaf) for leaf in leaves)
    levels = [level]

    while len(level) > 1:
        if len(level) % 2 == 1:
            level = [*level, level[-1]]
        next_level = []
        for idx in range(0, len(level), 2):
            next_level.append(sha256_hex(level[idx] + level[idx + 1]))
        level = next_level
        levels.append(level)

    return "sha256:" + level[0], levels


def build_merkle_catalog(catalog: dict[str, Any], source: str) -> dict[str, Any]:
    errors: list[str] = []

    if catalog.get("lattice_catalog") is not True:
        errors.append("not_lattice_catalog")
    if catalog.get("accepted_for_catalog") is not True:
        errors.append("catalog_not_accepted")
    if catalog.get("catalog_type") != "flat_hash_map":
        errors.append("catalog_type_not_flat_hash_map")

    for key in STICKY_FALSE:
        if catalog.get(key) is not False:
            errors.append(f"sticky_false_failed:{key}")

    entries = catalog.get("entries")
    if not isinstance(entries, dict) or not entries:
        errors.append("entries_missing_or_empty")
        entries = {}

    leaves = sorted(str(key) for key in entries.keys() if str(key).startswith("sha256:"))
    if len(leaves) != len(entries):
        errors.append("entry_key_not_sha256")

    root, levels = merkle_root(leaves)
    accepted = not errors and root is not None

    return {
        "lattice_merkle_catalog": True,
        "source_catalog": source,
        "source_catalog_type": catalog.get("catalog_type"),
        "leaf_count": len(leaves),
        "leaves": leaves,
        "merkle_root": root,
        "merkle_levels": levels,
        "accepted_for_merkle": accepted,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Merkle catalog from a flat lattice catalog.")
    parser.add_argument("catalog", type=Path)
    args = parser.parse_args()

    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    result = build_merkle_catalog(catalog, str(args.catalog))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["accepted_for_merkle"] else 1


if __name__ == "__main__":
    sys.exit(main())
