#!/usr/bin/env python3
"""Fail-closed load verification harness entrypoint.

This script creates the execution rail for LOAD_VERIFICATION_WITNESS_V0_1.
It does not claim LOAD_VERIFIED by itself.

Default behavior:
- emit a GOVERNANCE_GAP receipt candidate
- record missing witness conditions
- write transparency artifacts
- exit non-zero unless --allow-governance-gap-exit-zero is supplied

LOAD_VERIFIED promotion must be implemented by a later real verifier path that can
prove receipt integrity, transparency continuity, doctrine guards, and membrane state.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
from typing import Any


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def git_sha() -> str:
    return os.environ.get("GITHUB_SHA") or os.environ.get("CHAIN_HEAD") or "0" * 40


def build_receipt(args: argparse.Namespace) -> dict[str, Any]:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    run_id = args.run_id or f"harness-run-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    chain_head = git_sha()
    failed_conditions = [
        "real_load_runner_missing",
        "signed_receipt_integrity_missing",
        "independent_transparency_continuity_missing",
        "load_promotion_not_authorized",
    ]

    receipt_core = {
        "witness_version": "LOAD_VERIFICATION_WITNESS_V0_1",
        "run_id": run_id,
        "transform_version": args.transform_version,
        "target_qps": args.target_qps,
        "duration_min": args.duration_min,
        "gate_result": {
            "status": "GOVERNANCE_GAP",
            "timestamp": now,
            "checks_passed": 0,
            "drift_detected": False,
            "replay_surface": "AL → receiptos-base",
            "public_surface": "aligned",
        },
        "transparency_continuity": {
            "log_id": f"log-{chain_head}",
            "chain_head": chain_head,
            "merged_public_surface_sha": args.public_surface_sha,
            "continuous_from": args.continuous_from,
        },
        "transform_version_pinned": args.transform_version == "v0.1.0",
        "doctrine_guards": {
            "authority_false": True,
            "no_fake_green": True,
            "no_synthetic_pass": True,
            "no_public_load_badge_before_witness": True,
        },
        "membrane_unchanged": False,
        "failed_conditions": failed_conditions,
    }

    core_hash = sha256_hex(canonical_json(receipt_core))
    receipt_core["receipt_integrity"] = {
        "receipt_id": f"gap-{core_hash[:16]}",
        "receipt_sha256": core_hash,
        "jcs_canonical": True,
        "signature_verified": False,
    }
    return receipt_core


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run fail-closed load verification harness.")
    parser.add_argument("--transform-version", required=True)
    parser.add_argument("--target-qps", type=int, required=True)
    parser.add_argument("--duration-min", type=int, required=True)
    parser.add_argument("--run-id")
    parser.add_argument("--public-surface-sha", default="1539e812a5784dc0719c5c8b883615c73255d4c3")
    parser.add_argument("--continuous-from", default="1539e812a5784dc0719c5c8b883615c73255d4c3")
    parser.add_argument("--allow-governance-gap-exit-zero", action="store_true")
    args = parser.parse_args()

    receipt = build_receipt(args)
    run_id = receipt["run_id"]
    log_id = receipt["transparency_continuity"]["log_id"]
    chain_head = receipt["transparency_continuity"]["chain_head"]

    write_json(Path("receipts") / f"{run_id}.json", receipt)
    write_json(Path("transparency") / "log" / f"{log_id}.json", {
        "log_id": log_id,
        "run_id": run_id,
        "chain_head": chain_head,
        "status": receipt["gate_result"]["status"],
        "failed_conditions": receipt["failed_conditions"],
    })
    write_json(Path("transparency") / "index" / "chain_head.json", {
        "chain_head": chain_head,
        "latest_run_id": run_id,
        "latest_status": receipt["gate_result"]["status"],
    })

    print(json.dumps({
        "run_id": run_id,
        "receipt": f"receipts/{run_id}.json",
        "transparency_log": f"transparency/log/{log_id}.json",
        "chain_head": "transparency/index/chain_head.json",
        "status": receipt["gate_result"]["status"],
        "failed_conditions": receipt["failed_conditions"],
    }, indent=2))

    if receipt["gate_result"]["status"] == "LOAD_VERIFIED":
        return 0
    return 0 if args.allow_governance_gap_exit_zero else 2


if __name__ == "__main__":
    raise SystemExit(main())
