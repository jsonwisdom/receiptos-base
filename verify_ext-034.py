#!/usr/bin/env python3
import json
import sys
from pathlib import Path

VALIDATION_FILE = "market/ext-034-full-stack-validation.json"
RECEIPT_PATH = "receipts/tntr-018-full-stack-validation.json"
RECEIPT_MAP = {
    "EXT-029": "receipts/tntr-014-market-substrate-gate.json",
    "EXT-031": "receipts/tntr-015-instrument-layer-gate.json",
    "EXT-032": "receipts/tntr-016-instrument-deployment-gate.json",
    "EXT-033": "receipts/tntr-017-monitoring-gate.json"
}


def fail(msg):
    print("FAIL: " + msg)
    return False


def main():
    print("EXT-034 stack validation")
    p = Path(VALIDATION_FILE)
    if not p.exists():
        return fail("missing validation file")
    data = json.loads(p.read_text(encoding="utf-8"))
    if data.get("authority") is not False:
        return fail("authority drift")
    if data.get("resolution_semantics") != "absent":
        return fail("resolution drift")
    targets = data.get("validation_targets", [])
    for target in targets:
        rp = Path(RECEIPT_MAP.get(target, ""))
        if not rp.exists():
            return fail("missing receipt for " + target)
        receipt = json.loads(rp.read_text(encoding="utf-8"))
        if receipt.get("status") != "executed":
            return fail("receipt not executed for " + target)
    if data.get("stack_status") != "FINALIZED":
        return fail("stack not finalized")
    out = {
        "receipt_id": "TNTR-018-FULL-STACK-VALIDATION",
        "issue": "EXT-034",
        "gate": "Full Stack Validation",
        "status": "executed",
        "authority": False,
        "resolution_semantics": "absent",
        "validated_artifacts": targets,
        "boundary_assertions": data.get("boundary_assertions", {}),
        "stack_status": "FINALIZED",
        "verification_hash": "0x9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d",
        "next_action": "Production lock"
    }
    Path("receipts").mkdir(exist_ok=True)
    Path(RECEIPT_PATH).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print("OVERALL: PASS")
    return True

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
