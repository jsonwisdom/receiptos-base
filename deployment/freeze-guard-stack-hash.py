#!/usr/bin/env python3
import json, pathlib, hashlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RULE = ROOT / "deployment/stack-hash-rule-v1.json"

rule = json.loads(RULE.read_text())
h = hashlib.sha256()

for rel in rule["inputs"]:
    p = ROOT / rel
    if not p.exists():
        print(f"missing input: {rel}")
        sys.exit(2)
    h.update(rel.encode() + b"\0")
    h.update(p.read_bytes() + b"\0")

print(json.dumps({
    "status": "clean",
    "algorithm": rule["algorithm"],
    "stack_hash": h.hexdigest(),
    "authority": False,
    "resolution_semantics": "absent"
}, indent=2))
