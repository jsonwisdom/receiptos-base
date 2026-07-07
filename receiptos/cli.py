#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

EXIT = {
    "PASS": 0,
    "USAGE_ERROR": 1,
    "INPUT_MISSING": 2,
    "SCHEMA_FAIL": 3,
    "TREE_HASH_FAIL": 4,
    "MANIFEST_FAIL": 5,
    "INVARIANT_FAIL": 6,
    "REPLAY_FAIL": 7,
    "NON_DETERMINISTIC": 8,
    "INTERNAL_ERROR": 9,
}

VALID_TYPES = {
    "manifest_verify",
    "tree_hash",
    "schema_validate",
    "invariants_check",
    "replay_run",
    "replay_verify",
}

VALID_INVARIANTS = {
    "INV_READ_ONLY_WORKSPACE",
    "INV_COMMIT_RESOLVABLE",
    "INV_TREE_HASH_MATCH",
    "INV_SCHEMA_VALID",
    "INV_CANONICAL_SURFACES_PRESENT",
    "INV_DETERMINISTIC_OUTPUT",
    "INV_NON_AUTHORITY",
    "INV_FAILURE_EXPLICIT",
}

REQ = [
    "receipt_version",
    "receipt_type",
    "authority",
    "engine_id",
    "engine_version",
    "replay_invariants",
    "timestamp",
    "input_hash",
    "output_hash",
    "status",
]

HEX64 = re.compile(r"^[a-f0-9]{64}$")

def load(path):
    p = Path(path)
    if not p.exists():
        return None, EXIT["INPUT_MISSING"]
    try:
        return json.loads(p.read_text()), 0
    except Exception:
        return None, EXIT["SCHEMA_FAIL"]

def schema_validate(path):
    d, code = load(path)
    if code:
        return code

    for k in REQ:
        if k not in d:
            return EXIT["SCHEMA_FAIL"]

    if d["receipt_version"] != "0.1":
        return EXIT["SCHEMA_FAIL"]
    if d["receipt_type"] not in VALID_TYPES:
        return EXIT["SCHEMA_FAIL"]
    if d["authority"] is not False:
        return EXIT["SCHEMA_FAIL"]
    if d["engine_id"] != "receiptos-replay-engine":
        return EXIT["SCHEMA_FAIL"]
    if d["engine_version"] != "0.1":
        return EXIT["SCHEMA_FAIL"]
    if not isinstance(d["replay_invariants"], list) or not d["replay_invariants"]:
        return EXIT["SCHEMA_FAIL"]
    if not HEX64.match(d["input_hash"]) or not HEX64.match(d["output_hash"]):
        return EXIT["SCHEMA_FAIL"]
    if d["status"] not in ["PASS", "FAIL"]:
        return EXIT["SCHEMA_FAIL"]

    return EXIT["PASS"]

def replay_verify(path):
    code = schema_validate(path)
    if code:
        return code

    d, _ = load(path)

    for inv in d["replay_invariants"]:
        if inv not in VALID_INVARIANTS:
            return EXIT["INVARIANT_FAIL"]

    if d["output_hash"] == "0" * 64:
        return EXIT["TREE_HASH_FAIL"]

    return EXIT["PASS"]

def main(argv):
    if len(argv) != 4:
        return EXIT["USAGE_ERROR"]

    _, group, action, path = argv

    if group == "schema" and action == "validate":
        return schema_validate(path)

    if group == "replay" and action == "verify":
        return replay_verify(path)

    return EXIT["USAGE_ERROR"]

if __name__ == "__main__":
    sys.exit(main(sys.argv))
