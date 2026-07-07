#!/usr/bin/env python3
"""Standalone light inclusion verifier for lattice batch roots.

Input: leaf hash, sibling hash, sibling position, and expected root.
Output: proof_valid true/false.

This command verifies hash inclusion only. It does not load report bodies,
read catalogs, infer meaning, or mutate state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys


def normalize_hash(value: str) -> str:
    return value.strip().removeprefix("sha256:")


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_one_step(leaf_hash: str, sibling_hash: str, sibling_position: str, root_hash: str) -> bool:
    leaf = normalize_hash(leaf_hash)
    sibling = normalize_hash(sibling_hash)
    expected = normalize_hash(root_hash)

    if sibling_position == "left":
        computed = sha256_hex(sibling + leaf)
    elif sibling_position == "right":
        computed = sha256_hex(leaf + sibling)
    else:
        return False

    return computed == expected


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify one-step inclusion against a batch Merkle root.")
    parser.add_argument("--leaf", required=True)
    parser.add_argument("--sibling", required=True)
    parser.add_argument("--sibling-position", required=True, choices=["left", "right"])
    parser.add_argument("--root", required=True)
    args = parser.parse_args()

    proof_valid = verify_one_step(args.leaf, args.sibling, args.sibling_position, args.root)
    result = {
        "light_verifier": True,
        "proof_valid": proof_valid,
        "leaf_hash": args.leaf,
        "sibling_hash": args.sibling,
        "sibling_position": args.sibling_position,
        "merkle_root": args.root,
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
