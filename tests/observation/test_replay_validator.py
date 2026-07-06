#!/usr/bin/env python3
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPLAY_DIR = ROOT / "replay"
sys.path.insert(0, str(REPLAY_DIR))
from validate_replay_packet_v1 import determine_verdict  # noqa: E402

def parse_now(s):
    return datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(timezone.utc)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--now", default="2026-07-06T14:30:00Z")
    args=ap.parse_args()
    now=parse_now(args.now)

    failures=[]
    seen_packet_ids=set()
    seen_nonces=set()
    files=list((REPLAY_DIR/"fixtures").glob("*.packet.json"))+list((REPLAY_DIR/"fixtures"/"round3").glob("*.packet.json"))

    for path in sorted(files):
        packet=json.loads(path.read_text())
        expected=packet.get("expected_verdict")
        expected_reason=packet.get("expected_reason")
        actual, reason, tainted, warnings, policy_failures = determine_verdict(
            packet,
            now=now,
            seen_packet_ids=seen_packet_ids,
            seen_nonces=seen_nonces,
        )
        if expected and actual != expected:
            failures.append(f"{path.name}: expected {expected}, got {actual} reason={reason}")
        if expected_reason and reason != expected_reason:
            failures.append(f"{path.name}: expected reason {expected_reason}, got {reason}")

    if failures:
        print("FAILURES:")
        print("\n".join("  "+f for f in failures))
        return 1
    print("All Round 2 + Round 3 replay fixtures passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
