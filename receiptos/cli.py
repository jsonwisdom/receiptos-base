#!/usr/bin/env python3
import json
import re
import sys
import subprocess
import hashlib
from pathlib import Path

from jsonschema import Draft202012Validator

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


def canonical_tree_sha256(commit):
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--full-tree", commit],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return None
    canonical = "\n".join(sorted(result.stdout.splitlines()))
    return hashlib.sha256(canonical.encode()).hexdigest()

def manifest_fail(error, message):
    print(json.dumps({"valid": False, "error": error, "message": message}, sort_keys=True), file=sys.stderr)
    return EXIT["MANIFEST_FAIL"]

def manifest_verify(path):
    manifest, code = load(path)
    if code:
        return code

    schema_path = Path("schemas/manifest.schema.json")
    if not schema_path.exists():
        return EXIT["INPUT_MISSING"]

    try:
        schema = json.loads(schema_path.read_text())
        errors = sorted(Draft202012Validator(schema).iter_errors(manifest), key=lambda e: e.path)
        if errors:
            return EXIT["SCHEMA_FAIL"]
    except Exception:
        return EXIT["SCHEMA_FAIL"]

    commit = manifest["commit_sha"]
    tree_sha256 = canonical_tree_sha256(commit)
    if tree_sha256 is None:
        return manifest_fail("INV_COMMIT_RESOLVABLE", "commit is not resolvable")

    if tree_sha256 != manifest["tree_sha256"]:
        print(json.dumps({"valid": False, "error": "INV_TREE_HASH_MATCH", "message": "tree_sha256 mismatch"}, sort_keys=True), file=sys.stderr)
        return EXIT["TREE_HASH_FAIL"]

    for surface in manifest["canonical_surfaces"]:
        if subprocess.run(["git", "cat-file", "-e", f"{commit}:{surface}"], capture_output=True).returncode != 0:
            return manifest_fail("INV_CANONICAL_SURFACES_PRESENT", f"missing surface: {surface}")

    print(json.dumps({"valid": True, "commit_sha": commit, "tree_sha256": tree_sha256}, sort_keys=True))
    return EXIT["PASS"]

def schema_validate(path):
    d, code = load(path)
    if code:
        return code

    schema_path = Path("schemas/receipt.schema.json")
    if not schema_path.exists():
        return EXIT["INPUT_MISSING"]

    try:
        schema = json.loads(schema_path.read_text())
        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(d), key=lambda e: e.path)
        if errors:
            return EXIT["SCHEMA_FAIL"]
    except Exception:
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


def replay_run(path):
    code = schema_validate(path)
    if code:
        return code

    d, _ = load(path)

    for inv in d["replay_invariants"]:
        if inv not in VALID_INVARIANTS:
            return EXIT["INVARIANT_FAIL"]

    if d["output_hash"] == "0" * 64:
        return EXIT["TREE_HASH_FAIL"]

    print(json.dumps({
        "receipt_version": "0.1",
        "receipt_type": "replay_run",
        "authority": False,
        "engine_id": "receiptos-replay-engine",
        "engine_version": "0.1",
        "replay_invariants": d["replay_invariants"],
        "timestamp": d["timestamp"],
        "input_hash": d["input_hash"],
        "output_hash": d["output_hash"],
        "status": "PASS",
        "exit_code": 0,
        "errors": []
    }, sort_keys=True))

    return EXIT["PASS"]

def main(argv):
    if len(argv) != 4:
        return EXIT["USAGE_ERROR"]

    _, group, action, path = argv

    if group == "schema" and action == "validate":
        return schema_validate(path)

    if group == "manifest" and action == "verify":
        return manifest_verify(path)

    if group == "replay" and action == "verify":
        return replay_verify(path)

    if group == "replay" and action == "run":
        return replay_run(path)

    return EXIT["USAGE_ERROR"]

if __name__ == "__main__":
    sys.exit(main(sys.argv))
