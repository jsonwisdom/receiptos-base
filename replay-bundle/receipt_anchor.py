#!/usr/bin/env python3
import json, hashlib, sys
def canon(o): return json.dumps(o, sort_keys=True, separators=(",", ":"))
def h(s): return "0x" + hashlib.sha256(s.encode()).hexdigest()
receipt=json.load(open(sys.argv[1]))
print(json.dumps({
  "schema": "GoblinCourtVerificationReceiptV1",
  "receipt_hash": h(canon(receipt)),
  "authority": False
}, sort_keys=True, separators=(",", ":")))
