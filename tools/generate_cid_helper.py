#!/usr/bin/env python3
"""Deterministic metadata CID/helper report.

This helper does not mutate ledgers and does not grant authority. It compares a
local metadata JSON file against optional provenance and bridge records, then
emits a replayable JSON report.

Notes:
- `content_sha256` hashes the exact metadata file bytes.
- `canonical_sha256` hashes canonical JSON using sorted keys and compact
  separators.
- CID verification is conservative: when a CID is supplied in provenance or
  bridge data, the helper reports equality between declared values. It does not
  claim to recompute IPFS CIDs without an explicit CID library.
"""

import argparse
import hashlib
import json
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, Optional


def load_json(path: Optional[str]) -> Optional[Dict[str, Any]]:
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_strings(value: Any) -> Any:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [normalize_strings(v) for v in value]
    if isinstance(value, dict):
        return {str(k): normalize_strings(v) for k, v in value.items()}
    return value


def canonical_bytes(obj: Any) -> bytes:
    normalized = normalize_strings(obj)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prefixed(hex_value: str) -> str:
    return "sha256:" + hex_value


def strip_0x(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return value[2:] if value.startswith("0x") else value


def find_first(data: Optional[Dict[str, Any]], keys) -> Optional[str]:
    if not isinstance(data, dict):
        return None
    stack = [data]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            for key in keys:
                if key in cur and cur[key] not in (None, ""):
                    return str(cur[key])
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic CID/hash consistency report.")
    parser.add_argument("--metadata", required=True, help="Local metadata JSON path")
    parser.add_argument("--expected-cid", help="Expected CID, e.g. bafk...")
    parser.add_argument("--expected-metadata-hash", help="Expected sha256 hex or 0x-prefixed hex")
    parser.add_argument("--provenance", help="Optional provenance JSON path")
    parser.add_argument("--bridge", help="Optional bridge JSON path")
    parser.add_argument("--artifact-id", help="Optional artifact/collection address")
    args = parser.parse_args()

    metadata_path = Path(args.metadata)
    raw = metadata_path.read_bytes()
    metadata = json.loads(raw.decode("utf-8"))
    content_sha = sha256_hex(raw)
    canonical_sha = sha256_hex(canonical_bytes(metadata))

    provenance = load_json(args.provenance)
    bridge = load_json(args.bridge)

    provenance_cid = find_first(provenance, ("ipfsCid", "ipfs_cid", "metadataCid", "metadata_cid", "cid"))
    provenance_hash = find_first(provenance, ("metadataHash", "metadata_hash", "sha256_metadata", "canonical_hash"))
    bridge_cid = find_first(bridge, ("ipfsCid", "ipfs_cid", "metadataCid", "metadata_cid", "cid"))
    bridge_hash = find_first(bridge, ("metadataHash", "metadata_hash", "sha256_metadata", "canonical_hash"))

    expected_cid = args.expected_cid or provenance_cid or bridge_cid
    expected_hash = strip_0x(args.expected_metadata_hash or provenance_hash or bridge_hash)

    hash_candidates = {
        "content_sha256": content_sha,
        "canonical_sha256": canonical_sha,
    }

    metadata_hash_match = None
    if expected_hash:
        metadata_hash_match = expected_hash.lower() in {content_sha.lower(), canonical_sha.lower()}

    cid_match = None
    if expected_cid:
        cid_values = [v for v in (provenance_cid, bridge_cid, expected_cid) if v]
        cid_match = all(v == expected_cid for v in cid_values)

    bridge_metadata_match = None
    if bridge_hash:
        bridge_metadata_match = strip_0x(bridge_hash).lower() in {content_sha.lower(), canonical_sha.lower()}
    elif bridge_cid and expected_cid:
        bridge_metadata_match = bridge_cid == expected_cid

    provenance_metadata_match = None
    if provenance_hash:
        provenance_metadata_match = strip_0x(provenance_hash).lower() in {content_sha.lower(), canonical_sha.lower()}
    elif provenance_cid and expected_cid:
        provenance_metadata_match = provenance_cid == expected_cid

    checks = {
        "cid_match": cid_match,
        "metadata_hash_match": metadata_hash_match,
        "bridge_metadata_match": bridge_metadata_match,
        "provenance_metadata_match": provenance_metadata_match,
    }

    all_available_checks_pass = all(v is True for v in checks.values() if v is not None)
    any_checks_available = any(v is not None for v in checks.values())

    report = {
        "type": "cid_helper_report",
        "authority": False,
        "artifact_id": args.artifact_id,
        "metadata_path": str(metadata_path),
        "content_hash": prefixed(content_sha),
        "canonical_hash": prefixed(canonical_sha),
        "expected_cid": expected_cid,
        "expected_metadata_hash": prefixed(expected_hash.lower()) if expected_hash else None,
        "provenance_path": args.provenance,
        "bridge_path": args.bridge,
        "declared": {
            "provenance_cid": provenance_cid,
            "provenance_hash": provenance_hash,
            "bridge_cid": bridge_cid,
            "bridge_hash": bridge_hash,
        },
        "hash_candidates": hash_candidates,
        "checks": checks,
        "status": "VERIFIED" if any_checks_available and all_available_checks_pass else "BLOCKED",
        "blocked_reason": None if any_checks_available and all_available_checks_pass else "missing comparison target or mismatch",
    }

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "VERIFIED" else 1


if __name__ == "__main__":
    sys.exit(main())
