#!/usr/bin/env python3
"""Anchor-only consumer for storage-time readiness feeds.

Reads a subscription feed, validates it, and exports only storage-time anchor
records. It does not sort by timestamp or create timeline semantics.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
if str(AUDIT) not in sys.path:
    sys.path.insert(0, str(AUDIT))

from validate_subscription_feed import validate_feed  # noqa: E402


def consume_storage_anchors(feed: dict[str, Any], source: str) -> dict[str, Any]:
    validation = validate_feed(feed, source)
    if validation.get("feed_valid") is not True:
        return {
            "storage_anchor_consumer": True,
            "anchor_only": True,
            "feed_validated": False,
            "anchor_count": 0,
            "anchors": [],
            "authority": False,
            "truth_claim": False,
            "inference_performed": False,
            "state_mutated": False,
            "errors": ["feed_validation_failed", *validation.get("errors", [])],
        }

    anchors: list[dict[str, Any]] = []
    for entry in feed.get("entries", []):
        anchor = entry.get("storage_time_anchor")
        if anchor:
            anchors.append({
                "entry_id": entry.get("entry_id"),
                "entry_sequence": entry.get("entry_sequence"),
                "sequence_semantics": "storage_order_only",
                "batch_root": entry.get("batch_root"),
                "anchor_type": anchor.get("anchor_type"),
                "timestamp_utc": anchor.get("timestamp_utc"),
                "semantics": anchor.get("semantics"),
                "authority": False,
                "truth_claim": False,
                "inference_performed": False,
                "state_mutated": False,
            })

    return {
        "storage_anchor_consumer": True,
        "anchor_only": True,
        "feed_validated": True,
        "anchor_count": len(anchors),
        "anchors": anchors,
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "errors": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Consume storage-time anchors from a validated feed.")
    parser.add_argument("feed", type=Path)
    args = parser.parse_args()

    feed = json.loads(args.feed.read_text(encoding="utf-8"))
    result = consume_storage_anchors(feed, str(args.feed))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["feed_validated"] else 1


if __name__ == "__main__":
    sys.exit(main())
