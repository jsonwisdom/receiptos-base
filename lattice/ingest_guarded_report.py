#!/usr/bin/env python3
"""Guarded lattice ingestion for Witness replay reports.

This is the first lattice consumer pattern: admission gate only.
It calls the Witness Serialization Delta Guard before accepting a report.

It does not run simulation, infer truth, mutate state, promote authority,
or interpret domain meaning.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WITNESS = ROOT / "witness"
if str(WITNESS) not in sys.path:
    sys.path.insert(0, str(WITNESS))

from guard_replay_report import guard_report, read_expected_hash  # noqa: E402


def ingest_guarded_report(report: dict[str, Any], expected_hash: str | None, source: str) -> dict[str, Any]:
    guard = guard_report(report, expected_hash)
    accepted = bool(
        guard.get("consumer_safe") is True
        and guard.get("hash_match") is True
        and guard.get("authority") is False
        and guard.get("truth_claim") is False
        and guard.get("inference_performed") is False
        and guard.get("state_mutated") is False
    )

    reasons: list[str] = []
    if not accepted:
        if guard.get("consumer_safe") is not True:
            reasons.append("guard_consumer_safe_not_true")
        if guard.get("hash_match") is not True:
            reasons.append("guard_hash_match_not_true")
        if guard.get("authority") is not False:
            reasons.append("authority_not_false")
        if guard.get("truth_claim") is not False:
            reasons.append("truth_claim_not_false")
        if guard.get("inference_performed") is not False:
            reasons.append("inference_performed_not_false")
        if guard.get("state_mutated") is not False:
            reasons.append("state_mutated_not_false")

    return {
        "lattice_ingestion": True,
        "source_report": source,
        "source_report_hash": guard.get("computed_hash"),
        "ingestion_accepted": accepted,
        "guard_consumer_safe": bool(guard.get("consumer_safe")),
        "guard_hash_match": bool(guard.get("hash_match")),
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "reason_codes": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest a guarded Witness replay report into lattice boundary.")
    parser.add_argument("report", type=Path)
    parser.add_argument("--expect-file", type=Path)
    parser.add_argument("--expect-hash")
    args = parser.parse_args()

    if args.expect_file and args.expect_hash:
        parser.error("use either --expect-file or --expect-hash, not both")

    report = json.loads(args.report.read_text(encoding="utf-8"))
    expected_hash = read_expected_hash(args.expect_file, args.expect_hash)
    result = ingest_guarded_report(report, expected_hash, str(args.report))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ingestion_accepted"] else 1


if __name__ == "__main__":
    sys.exit(main())
