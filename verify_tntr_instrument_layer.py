#!/usr/bin/env python3
import json
import sys
from pathlib import Path

FORBIDDEN = ["TRUE", "FALSE", "YES", "NO", "RESOLVED", "GUILTY", "PROVEN", "VERDICT", "TRIBUNAL"]
FILES = [
    "market/tntr-instrument-layer-v0.json",
    "market/tntr-instrument.schema.json",
    "market/tntr-cro-001-instruments.json"
]
RECEIPT_PATH = "receipts/tntr-015-instrument-layer-gate.json"
ALLOWED_SOURCE_TYPES = {"replay_receipt", "mesh_receipt", "challenge_receipt"}


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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
    print("🔍 EXT-031 Instrument Layer Verification")
    loaded = {}
    for file_path in FILES:
        p = Path(file_path)
        if not p.exists():
            return fail(f"missing {file_path}")
        data = load(file_path)
        loaded[file_path] = data
        scan(data, file_path)
        if data.get("authority") is not False:
            return fail(f"authority must be false in {file_path}")
        print(f"PASS: {file_path}")

    layer = loaded["market/tntr-instrument-layer-v0.json"]
    if layer.get("truth_resolution") != "absent":
        return fail("layer truth_resolution must be absent")
    if layer.get("forbidden_semantics_enforced") is not True:
        return fail("forbidden_semantics_enforced must be true")

    instrument_map = loaded["market/tntr-cro-001-instruments.json"]
    if instrument_map.get("cro_id") != "TNTR-CRO-001":
        return fail("cro_id mismatch")
    if instrument_map.get("truth_resolution") != "absent":
        return fail("instrument map truth_resolution must be absent")

    instruments = instrument_map.get("allowed_instruments", [])
    if len(instruments) != 3:
        return fail("expected three instrument types")

    seen = []
    for inst in instruments:
        if inst.get("authority") is not False:
            return fail(f"instrument authority drift: {inst.get('instrument_id')}")
        if inst.get("resolution_semantics") != "absent":
            return fail(f"instrument resolution drift: {inst.get('instrument_id')}")
        if inst.get("forbidden_semantics_enforced") is not True:
            return fail(f"instrument forbidden lock missing: {inst.get('instrument_id')}")
        rule = inst.get("settlement_rule", {})
        if rule.get("source_type") not in ALLOWED_SOURCE_TYPES:
            return fail(f"invalid settlement source: {inst.get('instrument_id')}")
        if rule.get("mechanical_only") is not True:
            return fail(f"settlement must be mechanical only: {inst.get('instrument_id')}")
        seen.append(inst.get("instrument_type"))

    receipt = {
        "receipt_id": "TNTR-015-INSTRUMENT-LAYER-GATE",
        "issue": "EXT-031",
        "instrument_state": "ACTIVE",
        "instrument_authority": False,
        "instrument_resolution": "absent",
        "forbidden_semantics_enforced": True,
        "instrument_types": sorted(seen),
        "settlement_boundary": "receipts_only",
        "next_gate": "EXT-032"
    }
    Path("receipts").mkdir(exist_ok=True)
    with open(RECEIPT_PATH, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2)
        f.write("\n")
    print(f"PASS: receipt emitted {RECEIPT_PATH}")
    print("OVERALL: PASS")
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
