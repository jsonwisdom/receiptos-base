#!/usr/bin/env python3
import argparse, hashlib, json, sys
from pathlib import Path

def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":")).encode()

def root(leaves):
    nodes = [bytes.fromhex(x[2:]) for x in leaves]
    if not nodes:
        return "0x" + "0"*64
    while len(nodes) > 1:
        if len(nodes) % 2:
            nodes.append(nodes[-1])
        nodes = [hashlib.sha256(nodes[i] + nodes[i+1]).digest() for i in range(0, len(nodes), 2)]
    return "0x" + nodes[0].hex()

p = argparse.ArgumentParser()
p.add_argument("--write-proof", action="store_true")
p.add_argument("--write-expected-root", action="store_true")
p.add_argument("--strict", action="store_true")
args = p.parse_args()

script_dir = Path(__file__).resolve().parent
repo_root = script_dir.parents[1]
data = json.loads((repo_root / "creator-index.json").read_text())

artifacts = sorted(data["artifacts"], key=lambda a: a["artifact_id"])
locked = data["metadata"]["merkle_root"]
authority = data.get("authority")
membrane = data.get("membrane")

leaves = ["0x" + hashlib.sha256(canon(a)).hexdigest() for a in artifacts]
computed = root(leaves)

print(f"Computed root   : {computed}")
print(f"Locked root     : {locked}")
print(f"Root match      : {'PASS' if computed == locked else 'FAIL'}")
print(f"Authority       : {authority}")
print(f"Membrane        : {membrane}")
print(f"Artifact count  : {len(artifacts)}")

if args.strict:
    if authority is not False:
        sys.exit("FAIL: authority must be false")
    if membrane != "intact":
        sys.exit("FAIL: membrane must be intact")

if computed != locked:
    sys.exit("FAIL: root mismatch")

if args.write_proof:
    proof = {
        "round": "ROUND_009",
        "leaf_count": len(artifacts),
        "leaves": [{"artifact_id": a["artifact_id"], "leaf_hash": leaves[i]} for i, a in enumerate(artifacts)],
        "computed_root": computed,
        "locked_root": locked,
        "root_match": True,
        "authority": authority,
        "membrane": membrane
    }
    (script_dir / "merkle-proof.json").write_text(json.dumps(proof, indent=2) + "\n")

if args.write_expected_root:
    (script_dir / "expected-root.txt").write_text(computed + "\n")

print("READY_TO_SEAL")
