#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPLAY_DIR = ROOT / "replay"
FIXTURES_DIR = REPLAY_DIR / "fixtures"

sys.path.insert(0, str(REPLAY_DIR))
from validate_replay_packet_v1 import verdict  # noqa: E402

def main():
    failures = []
    for fixture_path in sorted(FIXTURES_DIR.glob("*.packet.json")):
        packet = json.loads(fixture_path.read_text())
        expected = packet.get("expected_verdict")
        if expected is None:
            failures.append(f"{fixture_path.name}: missing expected_verdict")
            continue
        actual, reason, tainted, warnings, policy_failures = verdict(packet)
        if actual != expected:
            failures.append(
                f"{fixture_path.name}: expected {expected}, got {actual} reason={reason} tainted={tainted}"
            )
    if failures:
        print("FAILURES:")
        print("\n".join(f"  {f}" for f in failures))
        return 1
    print("All Round 2 replay fixtures passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
