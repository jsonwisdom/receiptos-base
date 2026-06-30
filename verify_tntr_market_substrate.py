#!/usr/bin/env python3
import json
import sys
from pathlib import Path

FORBIDDEN_STRINGS = ["TRUE", "FALSE", "YES", "NO", "RESOLVED", "GUILTY", "PROVEN"]
TARGET_FILES = [
    "market/tntr-market-substrate-v0.json",
    "market/tntr-market-primitives.schema.json",
    "market/tntr-cro-001-market-map.json"
]
RECEIPT_PATH = "receipts/tntr-014-market-substrate-gate.json"

def deep_check_for_forbidden(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_path = f"{path}.{k}" if path else k
            deep_check_for_forbidden(v, new_path)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            deep_check_for_forbidden(item, f"{path}[{i}]")
    elif isinstance(obj, str):
        if obj.upper() in FORBIDDEN_STRINGS:
            raise ValueError(f"Forbidden string '{obj}' at {path or 'root'}")

def verify_substrate_gate():
    print("🔒 EXT-029 Verification: TNTR Market Substrate Gate")

    for file_path in TARGET_FILES:
        if not Path(file_path).exists():
            print(f"❌ Missing file: {file_path}")
            return False

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if data.get("authority") is not False:
            print(f"❌ authority must be false in {file_path}. Found: {data.get('authority')}")
            return False

        try:
            deep_check_for_forbidden(data, file_path)
        except ValueError as e:
            print(f"❌ Semantics violation: {e}")
            return False

        if "tntr-market-substrate-v0.json" in file_path:
            primitives = data.get("primitives", {})
            required = ["replay_status", "provenance_strength", "challenge"]
            if not all(p in primitives for p in required):
                print(f"❌ Missing required primitives in {file_path}")
                return False
            print(f"✅ {file_path} -> primitives locked")

        print(f"✅ {file_path} -> authority=false, no forbidden semantics")

    receipt_data = {
        "receipt_id": "TNTR-014-MARKET-SUBSTRATE-GATE",
        "issue": "EXT-029",
        "gate": "TNTR Market Substrate",
        "status": "executed",
        "authority": False,
        "market_authority": False,
        "truth_resolution": "absent",
        "boundary_conditions": "price≠truth | liquidity≠authority | QUERYABLE≠resolved | signal≠tribunal",
        "active_primitives": ["replay_status", "provenance_strength", "challenge"],
        "order_assertion": "market_substrate → replay_economic",
        "next_gate": "EXT-030",
        "forbidden_semantics_present": False
    }

    Path("receipts").mkdir(exist_ok=True)
    with open(RECEIPT_PATH, "w", encoding="utf-8") as f:
        json.dump(receipt_data, f, indent=2)
        f.write("\n")

    print(f"✅ Receipt generated: {RECEIPT_PATH}")
    print("🎯 EXT-029 Gate passed. Ready for EXT-030.")
    return True

if __name__ == "__main__":
    sys.exit(0 if verify_substrate_gate() else 1)
