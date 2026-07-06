#!/usr/bin/env python3
"""
Round 15: Deterministic Manifest Replay Harness.
Final Seal: Genesis, Receipt History, and Ledger State Verification.
"""

import json
from pathlib import Path
from ops.merkle import merkle_root
from observation_protocol.ingestion import IngestionEngine

def run_shadow_replay(receipt_dir: Path):
    shadow_engine = IngestionEngine(
        mode="REPLAY_ONLY",
        read_only=True
    )

    shadow_engine.replay(receipt_dir)

    return (
        shadow_engine.genesis_cid(),
        shadow_engine.get_receipt_hashes(),
        shadow_engine.final_state_root()
    )

def verify_replay(receipt_dir: Path, manifest_path: Path):
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    expected_genesis_cid = manifest["genesis_cid"]
    expected_receipt_merkle = manifest["receipt_merkle_root"]
    expected_state_root = manifest["ledger_state_root"]

    computed_genesis_cid, receipt_hashes, computed_state_root = run_shadow_replay(receipt_dir)

    if not receipt_hashes:
        raise SystemExit("FAIL: no receipts replayed")

    computed_receipt_merkle = merkle_root(receipt_hashes)

    match_genesis = computed_genesis_cid == expected_genesis_cid
    match_receipts = computed_receipt_merkle == expected_receipt_merkle
    match_state = computed_state_root == expected_state_root

    deterministic = match_genesis and match_receipts and match_state

    if not match_genesis:
        print("[!] Genesis Divergence")
        print(f"    Expected: {expected_genesis_cid}")
        print(f"    Observed: {computed_genesis_cid}")

    if not match_receipts:
        print("[!] History Divergence (Receipt Merkle)")
        print(f"    Expected: {expected_receipt_merkle}")
        print(f"    Observed: {computed_receipt_merkle}")

    if not match_state:
        print("[!] State Divergence (Ledger State Root)")
        print(f"    Expected: {expected_state_root}")
        print(f"    Observed: {computed_state_root}")

    print(f"""
Genesis CID........ {'PASS' if match_genesis else 'FAIL'}
Receipt Count...... {len(receipt_hashes)}
Receipt Merkle..... {'PASS' if match_receipts else 'FAIL'}
State Root......... {'PASS' if match_state else 'FAIL'}
Replay Version..... 15
Protocol Version... 1.0
FINAL RESULT
==============
{'DETERMINISTIC' if deterministic else 'FAIL'}
""")

    if not deterministic:
        raise SystemExit(1)

if __name__ == "__main__":
    verify_replay(
        receipt_dir=Path("/var/lib/receiptos/receipts/"),
        manifest_path=Path("/var/lib/receiptos/release/manifest.json")
    )
