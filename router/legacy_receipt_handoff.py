#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

HANDOFF_TYPE = "LEGACY_RECEIPT_HANDOFF_V0_1"
FREE_ONLY_RECEIPT_TYPE = "FREE_ONLY_THREE_SURFACE_RECEIPT_V0_2"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def receipt_type(path: Path) -> str | None:
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    value = data.get("receipt_type")
    return value if isinstance(value, str) else None


def json_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.rglob("*.json"))


def handoff(path: Path) -> dict[str, Any] | None:
    rtype = receipt_type(path)
    if rtype == FREE_ONLY_RECEIPT_TYPE:
        return None
    return {
        "handoff_type": HANDOFF_TYPE,
        "source_path": str(path),
        "source_receipt_type": rtype,
        "source_sha256": sha256_file(path),
        "route": "LEGACY_RECEIPT_ROUTER",
        "admissibility": "OUT_OF_SCOPE",
        "authority": False,
        "memory_safe": False,
        "mutation_performed": False,
        "alms_witness_indexed": False,
        "reason": "out-of-scope receipt preserved for separate policy handling",
        "next_allowed_actions": [
            "review under legacy policy",
            "define separate receipt-family schema"
        ],
        "forbidden_actions": [
            "mutate source receipt",
            "auto-upgrade receipt type",
            "invent missing evidence",
            "index as ALMS witness memory"
        ]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--output-dir", default="legacy-handoffs")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    out = Path(args.output_dir)
    records: list[dict[str, Any]] = []
    for raw in args.paths:
        path = Path(raw)
        if not path.exists():
            continue
        for item in json_files(path):
            record = handoff(item)
            if record is None:
                continue
            records.append(record)
            if not args.dry_run:
                out.mkdir(parents=True, exist_ok=True)
                target = out / f"{record['source_sha256']}.handoff.json"
                target.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(records, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
