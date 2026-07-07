#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\b")


def parse_claimed_time(payload: dict[str, Any]) -> dict[str, Any]:
    source = payload.get("source_provenance")
    text = payload.get("raw_text")
    errors: list[str] = []
    if not isinstance(source, str) or not source:
        errors.append("source_provenance_missing")
    if not isinstance(text, str) or not text:
        errors.append("raw_text_missing")
    match = PATTERN.search(text) if isinstance(text, str) else None
    claimed = match.group(0) if match else None
    if claimed is None:
        errors.append("claimed_timestamp_missing")
    return {
        "event_time_record": True,
        "parsed": not errors,
        "event_time_source": "external",
        "source_provenance": source,
        "claimed_timestamp_raw": claimed,
        "timezone_normalized": False,
        "storage_time_compared": False,
        "sorted": False,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": errors,
    }


def main() -> int:
    cli = argparse.ArgumentParser()
    cli.add_argument("payload", type=Path)
    args = cli.parse_args()
    payload = json.loads(args.payload.read_text(encoding="utf-8"))
    result = parse_claimed_time(payload)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["parsed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
