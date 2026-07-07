#!/usr/bin/env python3
"""
ROUND_013 global forest verifier.

Verifies global-manifest.json against canonical creator leaves.
- authority=false only
- algorithm=sha256 only
- leaves sorted by creator_id
- leaf hash = sha256(canonical JSON leaf)
- Merkle root uses duplicate-last rule for odd layers
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def canonical_json_bytes(obj: Any) -> bytes:
    """Deterministic JSON encoding for this repo's primitive-only receipts."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def merkle_root(leaves: List[str]) -> str:
    if not leaves:
        raise ValueError("global forest has no leaves")

    layer = leaves[:]
    while len(layer) > 1:
        next_layer = []
        for i in range(0, len(layer), 2):
            left = layer[i]
            right = layer[i + 1] if i + 1 < len(layer) else layer[i]
            next_layer.append(sha256_hex((left + right).encode("utf-8")))
        layer = next_layer
    return layer[0]


def load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"FAIL: missing {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"FAIL: invalid JSON in {path}: {exc}")


def main() -> int:
    repo_root = Path.cwd()
    manifest_path = repo_root / "global-manifest.json"
    leaves_dir = repo_root / "global-leaves"

    manifest = load_json(manifest_path)

    if manifest.get("algorithm") != "sha256":
        print(f"FAIL: algorithm must be sha256, got {manifest.get('algorithm')!r}")
        return 1

    leaves = manifest.get("leaves")
    if not isinstance(leaves, list) or not leaves:
        print("FAIL: manifest leaves must be a non-empty array")
        return 1

    sorted_leaves = sorted(leaves, key=lambda item: item.get("creator_id", ""))
    if leaves != sorted_leaves:
        print("FAIL: manifest leaves are not sorted by creator_id")
        return 1

    leaf_hashes: List[str] = []

    for leaf in sorted_leaves:
        creator_id = leaf.get("creator_id")
        if not creator_id:
            print("FAIL: leaf missing creator_id")
            return 1

        if leaf.get("authority") is not False:
            print(f"FAIL: {creator_id} authority must be false")
            return 1

        expected_path = leaves_dir / f"{creator_id}.json"
        file_leaf = load_json(expected_path)
        if file_leaf != leaf:
            print(f"FAIL: {expected_path} does not match manifest leaf for {creator_id}")
            return 1

        leaf_hash = sha256_hex(canonical_json_bytes(leaf))
        leaf_hashes.append(leaf_hash)
        print(f"PASS leaf {creator_id}: 0x{leaf_hash}")

    root = merkle_root(leaf_hashes)
    manifest_hash = sha256_hex(canonical_json_bytes(manifest))

    print(f"PASS global_root: 0x{root}")
    print(f"PASS manifest_hash: 0x{manifest_hash}")
    print("ROUND_013 VERIFICATION: PASS")

    receipt = {
        "algorithm": "sha256",
        "authority": False,
        "global_root": f"0x{root}",
        "manifest_hash": f"0x{manifest_hash}",
        "manifest_path": "global-manifest.json",
        "status": "PASS",
        "verifier": "tools/verify_global_forest.py",
        "verifier_version": "1.0",
        "version": "1.0",
    }

    receipt_path = repo_root / "evidence" / "receipts" / "global-forest-verification.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(
        json.dumps(receipt, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"PASS receipt: {receipt_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
