#!/usr/bin/env python3
"""Generate a fixture from the storage-time view command."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
if str(AUDIT) not in sys.path:
    sys.path.insert(0, str(AUDIT))

from storage_time_view import build_view  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate storage view fixture.")
    parser.add_argument("feed", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    feed = json.loads(args.feed.read_text(encoding="utf-8"))
    result = build_view(feed, str(args.feed))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["view_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
