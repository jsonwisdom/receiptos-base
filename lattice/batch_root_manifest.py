#!/usr/bin/env python3
"""Batch root manifest and inclusion proof tool.

Use case: light verification.

This tool builds a manifest from accepted flat catalogs and can verify a
single leaf against a Merkle root using an inclusion proof.

It operates on hashes only. It does not add timeline semantics,
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


def next_level(level: list[str]) -> list[str]:
    if len(level) % 2 == 1:
        level = [*level, level[-1]]
    return [sha256_hex(level[idx] + level[idx + 1]) for idx in range(0, len(level), 2)]


def merkle_levels(leaves: list[str]) -> list[list[str]]:
    if not leaves:
        return []
    level = sorted(normalize_hash(leaf) for leaf in leaves)
    levels = [level]
    while len(level) > 1:
        level = next_level(level)
        levels.append(level)
    return levels


def collect_catalog_leaves(catalog: dict[str, Any], source: str) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    records: list[dict[str, Any]] = []

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
        return records, errors

    for leaf, entry in entries.items():
        if not isinstance(leaf, str) or not leaf.startswith("sha256:"):
            errors.append(f"{source}:entry_key_not_sha256")
            continue
        records.append({
            "leaf_hash": leaf,
            "catalog": source,
            "source_report": entry.get("source_report") if isinstance(entry, dict) else None,
            "source_artifact": entry.get("source_artifact") if isinstance(entry, dict) else None,
        })

    return records, errors


def proof_for_leaf(leaves: list[str], target_leaf: str) -> list[dict[str, str]]:
    target = normalize_hash(target_leaf)
    level = sorted(normalize_hash(leaf) for leaf in leaves)
    if target not in level:
        raise ValueError("target_leaf_missing")

    index = level.index(target)
    proof: list[dict[str, str]] = []

    while len(level) > 1:
        working = level if len(level) % 2 == 0 else [*level, level[-1]]
        sibling_index = index - 1 if index % 2 == 1 else index + 1
        sibling = working[sibling_index]
        position = "left" if sibling_index < index else "right"
        proof.append({"sibling_position": position, "sibling_hash": "sha256:" + sibling})
        level = next_level(level)
        index = index // 2

    return proof


def verify_proof(leaf_hash: str, root_hash: str, proof: list[dict[str, str]]) -> bool:
    current = normalize_hash(leaf_hash)
    expected_root = normalize_hash(root_hash)
    for step in proof:
        sibling = normalize_hash(step["sibling_hash"])
        if step["sibling_position"] == "left":
            current = sha256_hex(sibling + current)
        elif step["sibling_position"] == "right":
            current = sha256_hex(current + sibling)
        else:
            return False
    return current == expected_root


def build_manifest(catalogs: list[tuple[str, dict[str, Any]]]) -> dict[str, Any]:
    errors: list[str] = []
    records: list[dict[str, Any]] = []
    for source, catalog in catalogs:
        catalog_records, catalog_errors = collect_catalog_leaves(catalog, source)
        records.extend(catalog_records)
        errors.extend(catalog_errors)

    leaves = [record["leaf_hash"] for record in records]
    unique_leaves = sorted(set(leaves))
    if len(unique_leaves) != len(leaves):
        errors.append("duplicate_leaf_hash")

    levels = merkle_levels(unique_leaves)
    root = "sha256:" + levels[-1][0] if levels else None

    proofs = {}
    if root:
        for leaf in unique_leaves:
            proofs[leaf] = proof_for_leaf(unique_leaves, leaf)

    accepted = not errors and root is not None
    return {
        "batch_root_manifest": True,
        "manifest_use_case": "light_verification",
        "leaf_count": len(unique_leaves),
        "leaves": unique_leaves,
        "leaf_metadata": records,
        "merkle_root": root,
        "proofs": proofs,
        "accepted_for_manifest": accepted,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or verify a batch-root manifest.")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("catalogs", type=Path, nargs="+")

    verify = sub.add_parser("verify")
    verify.add_argument("manifest", type=Path)
    verify.add_argument("leaf_hash")

    args = parser.parse_args()

    if args.command == "build":
        catalogs = [(str(path), json.loads(path.read_text(encoding="utf-8"))) for path in args.catalogs]
        result = build_manifest(catalogs)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["accepted_for_manifest"] else 1

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    root = manifest.get("merkle_root")
    proofs = manifest.get("proofs", {})
    proof = proofs.get(args.leaf_hash)
    proof_valid = isinstance(root, str) and isinstance(proof, list) and verify_proof(args.leaf_hash, root, proof)
    result = {
        "light_verifier": True,
        "leaf_hash": args.leaf_hash,
        "merkle_root": root,
        "proof_valid": proof_valid,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": [] if proof_valid else ["proof_invalid"],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if proof_valid else 1


if __name__ == "__main__":
    sys.exit(main())
