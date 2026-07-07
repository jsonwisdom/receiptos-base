#!/usr/bin/env python3
import json, hashlib, sys
from pathlib import Path

ROOT = Path("receipts")
OUT = Path("artifacts/receipt_inventory.json")

PLACEHOLDERS = ["...", "MATCH", "full report above", "\"All\""]

def sha256_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def scan_placeholders(text):
    return [x for x in PLACEHOLDERS if x in text]

def main():
    if not ROOT.exists():
        print("FAIL: receipts/ missing")
        return 1

    items = []
    errors = []

    for p in sorted(ROOT.glob("*.json")):
        text = p.read_text(errors="replace")
        try:
            data = json.loads(text)
        except Exception as e:
            errors.append({"path": str(p), "error": str(e)})
            continue

        item = {
            "path": str(p),
            "sha256": sha256_file(p),
            "top_level_keys": sorted(data.keys()),
            "authority": data.get("authority", None),
            "truth_claim": data.get("truth_claim", None),
            "placeholder_hits": scan_placeholders(text),
            "schema": data.get("schema", None),
            "version": data.get("version", None),
            "receipt_id": data.get("receipt_id", data.get("artifact_id", None))
        }

        if data.get("authority", False) is not False:
            item["authority_flag"] = "NON_FALSE_OR_MISSING"

        if "truth_claim" in data and data.get("truth_claim") is not False:
            item["truth_claim_flag"] = "NON_FALSE"

        items.append(item)

    OUT.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "receipt_inventory_version": "0.1",
        "source": "receipts/*.json",
        "receipt_count": len(items),
        "json_errors": errors,
        "placeholder_files": [i for i in items if i["placeholder_hits"]],
        "authority_non_false_or_missing": [
            i for i in items if i.get("authority_flag")
        ],
        "truth_claim_non_false": [
            i for i in items if i.get("truth_claim_flag")
        ],
        "receipts": items
    }

    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    print(f"RECEIPT_INVENTORY_WRITTEN={OUT}")
    print(f"receipt_count={len(items)}")
    print(f"json_errors={len(errors)}")
    print(f"placeholder_files={len(report['placeholder_files'])}")
    print(f"authority_non_false_or_missing={len(report['authority_non_false_or_missing'])}")
    print(f"truth_claim_non_false={len(report['truth_claim_non_false'])}")

    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
