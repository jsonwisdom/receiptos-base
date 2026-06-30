#!/usr/bin/env python3
"""Witness replay runner for ReceiptOS / ESG-001 frames.

Witness replay consumes ReceiptOS frames as representation artifacts only.
It composes over the base validator and optional profile validators, then
emits a deterministic replay report.

It does not infer truth, mutate graph state, adjudicate evidence, verify
on-chain finality, or promote authority.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from validate_receiptos_frame import validate_frame  # noqa: E402


def load_profile_validator(profile: str):
    if profile == "eas-v1":
        from validate_eas_profile_frame import validate_eas_profile  # noqa: E402

        return validate_eas_profile
    raise ValueError(f"unsupported_profile:{profile}")


def replay_frame(
    frame: dict[str, Any],
    *,
    profile: str | None,
    max_skew_seconds: int,
    disable_timestamp: bool,
) -> dict[str, Any]:
    base = validate_frame(frame, max_skew_seconds, disable_timestamp)

    profile_result = None
    profile_conformant = None
    profile_errors: list[str] = []
    if profile:
        validator = load_profile_validator(profile)
        profile_result = validator(frame)
        profile_conformant = bool(profile_result.get("eas_profile_valid"))
        profile_errors = list(profile_result.get("errors", []))

    report = {
        "witness_replay": True,
        "frame_loaded": True,
        "frame_type": frame.get("frame_type"),
        "profile": profile,
        "base_conformant": bool(base.get("conformant")),
        "profile_conformant": profile_conformant,
        "conformant": bool(base.get("conformant")) and (profile_conformant is not False),
        "hash_match": bool(base.get("hash_match")),
        "nonce_well_formed": bool(base.get("nonce_well_formed")),
        "timestamp_within_bounds": bool(base.get("timestamp_within_bounds")),
        "timestamp_check_disabled": bool(base.get("timestamp_check_disabled")),
        "signature_envelope_valid": bool(base.get("signature_envelope_valid")),
        "authority": False,
        "truth_claim": False,
        "inference_performed": False,
        "state_mutated": False,
        "base_errors": list(base.get("errors", [])),
        "profile_errors": profile_errors,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Witness replay a ReceiptOS / ESG-001 frame.")
    parser.add_argument("frame", type=Path)
    parser.add_argument("--profile", choices=["eas-v1"], default=None)
    parser.add_argument("--max-skew-seconds", type=int, default=300)
    parser.add_argument(
        "--disable-timestamp",
        action="store_true",
        help="Bypass timestamp freshness check for deterministic fixtures.",
    )
    args = parser.parse_args()

    frame = json.loads(args.frame.read_text(encoding="utf-8"))
    report = replay_frame(
        frame,
        profile=args.profile,
        max_skew_seconds=args.max_skew_seconds,
        disable_timestamp=args.disable_timestamp,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["conformant"] else 1


if __name__ == "__main__":
    sys.exit(main())
