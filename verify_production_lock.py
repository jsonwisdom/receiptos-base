#!/usr/bin/env python3
import json
import sys
from pathlib import Path

MANIFEST = "deployment/tntr-v1-production-manifest.json"
RECEIPT = "receipts/tntr-019-production-lock.json"
FORBIDDEN = ["TRUE", "FALSE", "YES", "NO", "RESOLVED", "GUILTY", "PROVEN", "VERDICT", "TRIBUNAL"]


def scan(obj, path="root"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            scan(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            scan(item, f"{path}[{i}]")
    elif isinstance(obj, str) and obj.upper() in FORBIDDEN:
        raise ValueError(f"forbidden semantic {obj} at {path}")


def fail(msg):
    print("FAIL: " + msg)
    return False


def main():
    print("TNTR-v1 production lock verification")
    p = Path(MANIFEST)
    if not p.exists():
        return fail("missing production manifest")
    data = json.loads(p.read_text(encoding="utf-8"))
    scan(data, MANIFEST)
    if data.get("authority") is not False:
        return fail("authority drift")
    if data.get("resolution_semantics") != "absent":
        return fail("resolution drift")
    gates = data.get("gates", {})
    for gate_id, gate_data in gates.items():
        if gate_data.get("status") != "executed":
            return fail("gate not executed: " + gate_id)
        rp = Path(gate_data.get("receipt", ""))
        if not rp.exists():
            return fail("missing receipt for " + gate_id)
        receipt = json.loads(rp.read_text(encoding="utf-8"))
        if receipt.get("status") != "executed":
            return fail("receipt not executed for " + gate_id)
    if not data.get("stack_hash"):
        return fail("missing stack hash")
    out = {
        "receipt_id": "TNTR-019-PRODUCTION-LOCK",
        "issue": "PRODUCTION-LOCK",
        "version": "TNTR-v1-final",
        "status": "PRODUCTION",
        "authority": False,
        "resolution_semantics": "absent",
        "stack_hash": data["stack_hash"],
        "deployment_time": data["deployment_time"],
        "gates_locked": list(gates.keys()),
        "deferred_extensions": [data.get("deferred_gate", {}).get("issue")],
        "verification_hash": data["verification_hash"]
    }
    Path("receipts").mkdir(exist_ok=True)
    Path(RECEIPT).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print("OVERALL: PASS")
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
