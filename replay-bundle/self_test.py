#!/usr/bin/env python3
import json, subprocess, sys, platform, hashlib

EXPECTED="0xdf0e9e385ad3f3ad610f3e4cae6506ab2c83fa5beb75dd921402070c4a80603f"

def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"))

def main():
    subprocess.check_call(["python3","verify.py","--proof","proofs/proof.json"], stdout=open("receipts/selftest-receipt.json","w"))
    subprocess.check_call(["python3","receipt_anchor.py","receipts/source-receipt.json"], stdout=open("receipts/selftest-anchor.json","w"))

    anchor=json.load(open("receipts/selftest-anchor.json"))
    actual=anchor["receipt_hash"]

    out={
      "status": "PASS" if actual == EXPECTED else "FAIL",
      "round": "021",
      "python": platform.python_version(),
      "expected_receipt_hash": EXPECTED,
      "actual_receipt_hash": actual,
      "authority": False
    }

    print(canon(out))
    return 0 if out["status"]=="PASS" else 1

if __name__=="__main__":
    sys.exit(main())
