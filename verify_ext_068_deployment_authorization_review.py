#!/usr/bin/env python3
import json, hashlib, pathlib, sys

ROOT = pathlib.Path("receipts")
NEEDED = ["EXT-064", "EXT-065", "EXT-066", "EXT-067", "EXT-068"]

def load_json(p):
    try:
        return json.loads(p.read_text())
    except Exception:
        return None

found = {}
for p in ROOT.glob("*.json"):
    data = load_json(p)
    if isinstance(data, dict):
        issue = data.get("issue")
        if issue in NEEDED:
            found[issue] = p

missing = [x for x in NEEDED if x not in found]
if missing:
    print("EXT-068 FAIL: missing issue artifacts:", ", ".join(missing))
    print("searched receipts/*.json")
    sys.exit(1)

review = load_json(found["EXT-068"])

must_equal = {
  "authorization_granted": False,
  "deployment_executed": False,
  "runtime_mode": "witness_only",
  "authority": False,
  "truth_claim": False,
  "resolution_semantics": "absent",
  "badge_power": 0,
  "vote_power": 0,
  "governance_action_allowed": False,
  "promotion_allowed": False,
  "transfer_governance_rights": False,
  "review_complete": True
}

for k,v in must_equal.items():
    if review.get(k) != v:
        print(f"EXT-068 FAIL: {k} expected {v!r}, got {review.get(k)!r}")
        sys.exit(1)

digests = {
    issue: hashlib.sha256(path.read_bytes()).hexdigest()
    for issue, path in sorted(found.items())
}

print("EXT-068 PASS:")
print("deployment authorization reviewed; authorization not granted; deployment not executed; policy conformity maintained; witness membrane preserved; authority=false; truth_claim=false; vote_power=0")
print(json.dumps({"artifacts": {k: str(v) for k,v in sorted(found.items())}, "deterministic_digests": digests}, indent=2))
