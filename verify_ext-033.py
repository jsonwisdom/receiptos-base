#!/usr/bin/env python3
import json
import sys
from pathlib import Path

SPEC = "market/ext-033-monitoring-adjustment.json"
RECEIPT = "receipts/tntr-017-monitoring-gate.json"
FORBIDDEN = ["TRUE", "FALSE", "YES", "NO", "RESOLVED", "GUILTY", "PROVEN", "VERDICT", "TRIBUNAL"]
REQUIRED_MONITORS = {"price_signal", "liquidity_signal", "settlement_behavior"}


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
    print("🔍 EXT-033 Monitoring & Adjustment Verification")
    path = Path(SPEC)
    if not path.exists():
        return fail(f"missing {SPEC}")

    data = json.loads(path.read_text(encoding="utf-8"))
    scan(data, SPEC)

    if data.get("authority") is not False:
        return fail("authority must be false")
    if data.get("resolution_semantics") != "absent":
        return fail("resolution_semantics must be absent")
    if data.get("monitoring_authority") is not False:
        return fail("monitoring_authority must be false")
    if data.get("forbidden_semantics_enforced") is not True:
        return fail("forbidden lock missing")

    monitoring = data.get("monitoring", {})
    if set(monitoring.keys()) != REQUIRED_MONITORS:
        return fail("monitoring fields mismatch")
    for name, cfg in monitoring.items():
        if "drift_detection" not in cfg or "assertion" not in cfg:
            return fail(f"missing drift hook: {name}")

    receipt = {
        "receipt_id": "TNTR-017-MONITORING-GATE",
        "issue": "EXT-033",
        "gate": "Monitoring & Adjustment",
        "status": "executed",
        "authority": False,
        "monitoring_authority": False,
        "resolution_semantics": "absent",
        "monitoring_fields": sorted(monitoring.keys()),
        "adjustment_parameters": data.get("adjustment_parameters", {}),
        "forbidden_semantics_enforced": True,
        "next_gate": "EXT-034"
    }
    Path("receipts").mkdir(exist_ok=True)
    Path(RECEIPT).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: receipt emitted {RECEIPT}")
    print("OVERALL: PASS")
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
