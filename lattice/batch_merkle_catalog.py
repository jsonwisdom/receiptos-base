#!/usr/bin/env python3
"""Combined multi-leaf Merkle catalog for accepted flat hash catalogs.

Use case: batch verification.

Input: one or more flat hash catalog artifacts.
Output: one Merkle root over all accepted report hashes.

This layer aggregates hashes only. It does not add timeline semantics,
relationships, scoring, clustering, simulation, graph mutation, authority,
or truth.
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


def collect_leaves(catalog: dict[str, Any], source: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    leaves: list[str] = []

    if catalog.get("lattice_catalog") is not True:
        errors.append(f"{source}:not_lattice_catalog")
    if catalog.get("accepted_for_catalog") is not True:
        errors.append(f"{source}:catalog_not_accepted")
    if catalog.get("catalog_type") != "flat_hash_map":
        errors.append(f"{source}:catalog_type_not_flat_hash_map")

    for key in STICKY_FALSE:
        if catalog.get(key) is not False:
            errors.append(f"{source}:sticky_false_failed:{key}")

    entries = catalog.get("entries")
    if not isinstance(entries, dict) or not entries:
        errors.append(f"{source}:entries_missing_or_empty")
        return leaves, errors

    for key in entries.keys():
        if isinstance(key, str) and key.startswith("sha256:"):
            leaves.append(key)
        else:
            errors.append(f"{source}:entry_key_not_sha256")

    return leaves, errors


def build_batch_merkle(catalogs: list[tuple[str, dict[str, Any]]]) -> dict[str, Any]:
    errors: list[str] = []
    leaves: list[str] = []
    sources: list[str] = []

    for source, catalog in catalogs:
        catalog_leaves, catalog_errors = collect_leaves(catalog, source)
        leaves.extend(catalog_leaves)
        errors.extend(catalog_errors)
        sources.append(source)

    unique_leaves = sorted(set(leaves))
    if len(unique_leaves) != len(leaves):
        errors.append("duplicate_leaf_hash")

    root, levels = merkle_root(unique_leaves)
    accepted = not errors and root is not None

    return {
        "lattice_batch_merkle_catalog": True,
        "batch_use_case": "batch_verification",
        "source_catalogs": sources,
        "leaf_count": len(unique_leaves),
        "leaves": unique_leaves,
        "merkle_root": root,
        "merkle_levels": levels,
        "accepted_for_batch_merkle": accepted,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a combined Merkle catalog from flat lattice catalogs.")
    parser.add_argument("catalogs", type=Path, nargs="+")
    args = parser.parse_args()

    catalogs = [(str(path), json.loads(path.read_text(encoding="utf-8"))) for path in args.catalogs]
    result = build_batch_merkle(catalogs)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["accepted_for_batch_merkle"] else 1


if __name__ == "__main__":
    sys.exit(main())
