#!/usr/bin/env python3
import argparse, json, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPLAY_DIR = ROOT / "replay"
sys.path.insert(0, str(REPLAY_DIR))
from validate_replay_packet_v1 import verdict  # noqa: E402

def parse_now(s):
    return datetime.fromisoformat(s.replace("Z","+00:00"))

def replay_guard(packet, now):
    for k in ["packet_id","nonce","issued_at","expires_at","replay_window_seconds"]:
        if k not in packet:
            return "INDETERMINATE", f"missing_{k}"
    try:
        issued=parse_now(packet["issued_at"])
        expires=parse_now(packet["expires_at"])
        window=timedelta(seconds=int(packet["replay_window_seconds"]))
    except Exception:
        return "INDETERMINATE", "invalid_replay_time_fields"
    if now < issued - window:
        return "INDETERMINATE", "future_issued_at"
    if now > expires + window:
        return "FAIL", "replay_window_exceeded"
    return None, None

def eval_packet(packet, now):
    g_v, g_r = replay_guard(packet, now)
    if g_v:
        return g_v, g_r, False
    v,r,t,w,p = verdict(packet)
    if r == "hash_verified":
        r = "replay_verified"
    return v,r,t

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--now", default="2026-07-06T14:30:00Z")
    args=ap.parse_args()
    now=parse_now(args.now)

    failures=[]
    seen=set()
    files=list((REPLAY_DIR/"fixtures").glob("*.packet.json"))+list((REPLAY_DIR/"fixtures"/"round3").glob("*.packet.json"))

    for path in sorted(files):
        packet=json.loads(path.read_text())
        pid=packet.get("packet_id")
        expected=packet.get("expected_verdict")
        expected_reason=packet.get("expected_reason")
        is_round3 = "round3" in path.parts
        if is_round3:
            if pid:
                if pid in seen:
                    actual, reason, tainted = "FAIL", "duplicate_packet_id", False
                else:
                    seen.add(pid)
                    actual, reason, tainted = eval_packet(packet, now)
            else:
                actual, reason, tainted = eval_packet(packet, now)
        else:
            actual, reason, tainted = verdict(packet)[:3]
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
