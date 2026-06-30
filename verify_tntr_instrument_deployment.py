#!/usr/bin/env python3
import json
import sys
from pathlib import Path

DEPLOYMENT = "market/instruments/tntr-instrument-deployment-v0.json"
RECEIPT = "receipts/tntr-016-instrument-deployment-gate.json"
FORBIDDEN = ["TRUE", "FALSE", "YES", "NO", "RESOLVED", "GUILTY", "PROVEN", "VERDICT", "TRIBUNAL"]
ALLOWED_TYPES = {"replay_future", "provenance_strength_note", "challenge_instrument"}
ALLOWED_SOURCES = {"replay_receipt", "mesh_receipt", "challenge_receipt"}


def scan(obj, path="root"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            scan(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            scan(v, f"{path}[{i}]")
    elif isinstance(obj, str) and obj.upper() in FORBIDDEN:
        raise ValueError(f"forbidden semantic {obj} at {path}")


def fail(msg):
    print(f"FAIL: {msg}")
    return False


def main():
    print("🔍 EXT-032 Instrument Deployment Verification")
    path = Path(DEPLOYMENT)
    if not path.exists():
        return fail(f"missing {DEPLOYMENT}")

    data = json.loads(path.read_text(encoding="utf-8"))
    scan(data, DEPLOYMENT)

    if data.get("authority") is not False:
        return fail("deployment authority must be false")
    if data.get("resolution_semantics") != "absent":
        return fail("deployment resolution_semantics must be absent")
    if data.get("forbidden_semantics_enforced") is not True:
        return fail("forbidden lock missing")

    instruments = data.get("instruments", [])
    if len(instruments) != 3:
        return fail("expected three deployed instruments")

    seen = []
    for inst in instruments:
        if inst.get("instrument_type") not in ALLOWED_TYPES:
            return fail(f"invalid instrument type: {inst.get('instrument_type')}")
        if inst.get("authority") is not False:
            return fail(f"authority drift: {inst.get('instrument_id')}")
        if inst.get("resolution_semantics") != "absent":
            return fail(f"resolution drift: {inst.get('instrument_id')}")
        if inst.get("forbidden_semantics_enforced") is not True:
            return fail(f"forbidden lock missing: {inst.get('instrument_id')}")
        rule = inst.get("settlement_rule", {})
        if rule.get("source_type") not in ALLOWED_SOURCES:
            return fail(f"invalid settlement source: {inst.get('instrument_id')}")
        if rule.get("mechanical_only") is not True:
            return fail(f"settlement not mechanical only: {inst.get('instrument_id')}")
        seen.append(inst.get("instrument_type"))

    receipt = {
        "receipt_id": "TNTR-016-INSTRUMENT-DEPLOYMENT-GATE",
        "issue": "EXT-032",
        "gate": "Instrument Deployment",
        "status": "executed",
        "instrument_authority": False,
        "instrument_resolution": "absent",
        "forbidden_semantics_enforced": True,
        "instrument_types": sorted(seen),
        "settlement_boundary": "mechanical_receipts_only",
        "next_gate": "EXT-033"
    }
    Path("receipts").mkdir(exist_ok=True)
    Path(RECEIPT).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: receipt emitted {RECEIPT}")
    print("OVERALL: PASS")
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
