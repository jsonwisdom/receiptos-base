#!/usr/bin/env python3
"""LLM Radar intake runner.

Directory sources are signals only. This runner snapshots the watchlist,
emits a receipt-backed alert ledger entry, and never promotes a model into
model_registry.json without benchmark replay evidence.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
from typing import Any, Dict

VERSION = "LLM_RADAR_INTAKE_V1"
GENESIS_PREV_RECEIPT_HASH = "sha256:" + "0" * 64


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: pathlib.Path) -> list[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def last_hash(rows: list[Dict[str, Any]]) -> str:
    if not rows:
        return GENESIS_PREV_RECEIPT_HASH
    value = rows[-1].get("receipt_hash")
    return value if isinstance(value, str) else GENESIS_PREV_RECEIPT_HASH


def receipt_hash(receipt: Dict[str, Any]) -> str:
    basis = dict(receipt)
    basis["receipt_hash"] = None
    return sha256_bytes(canonical_json(basis).encode("utf-8"))


def append_jsonl(path: pathlib.Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(canonical_json(row) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def main() -> int:
    parser = argparse.ArgumentParser(description="LLM Radar intake receipt runner")
    parser.add_argument("--watchlist", default="models/free_llm_watchlist.json", type=pathlib.Path)
    parser.add_argument("--registry", default="models/model_registry.json", type=pathlib.Path)
    parser.add_argument("--ledger", default="receipts/model_alerts.jsonl", type=pathlib.Path)
    parser.add_argument("--print", action="store_true")
    args = parser.parse_args()

    watchlist_bytes = args.watchlist.read_bytes()
    registry_bytes = args.registry.read_bytes()
    watchlist = load_json(args.watchlist)
    registry = load_json(args.registry)
    rows = load_jsonl(args.ledger)

    receipt: Dict[str, Any] = {
        "version": VERSION,
        "created_at": utc_now(),
        "event_type": "LLM_DIRECTORY_SIGNAL_INTAKE",
        "watchlist_path": str(args.watchlist),
        "watchlist_hash": sha256_bytes(watchlist_bytes),
        "registry_path": str(args.registry),
        "registry_hash_before": sha256_bytes(registry_bytes),
        "sources_seen": [source.get("source_id") for source in watchlist.get("sources", [])],
        "providers_seen": [provider.get("provider") for provider in watchlist.get("providers_to_watch", [])],
        "verified_registry_count": len(registry.get("providers", [])),
        "action": "ALERT_MANUAL_REVIEW_REQUIRED",
        "promotion_allowed": False,
        "prev_receipt_hash": last_hash(rows),
        "receipt_hash": None,
        "invariants": {
            "directory_is_signal": True,
            "receiptos_replay_is_verification": True,
            "authority": False,
            "truth_claim": False
        }
    }
    receipt["receipt_hash"] = receipt_hash(receipt)
    append_jsonl(args.ledger, receipt)

    print(f"LLM_RADAR_STATUS=ALERT_MANUAL_REVIEW_REQUIRED")
    print(f"LLM_RADAR_RECEIPT_HASH={receipt['receipt_hash']}")
    print(f"LLM_RADAR_WATCHLIST_HASH={receipt['watchlist_hash']}")
    if args.print:
        print(canonical_json(receipt))

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write("status=ALERT_MANUAL_REVIEW_REQUIRED\n")
            handle.write(f"receipt_hash={receipt['receipt_hash']}\n")
            handle.write(f"watchlist_hash={receipt['watchlist_hash']}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
