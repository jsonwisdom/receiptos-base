#!/usr/bin/env python3
import json, hashlib, re
from pathlib import Path

def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def h(s):
    return hashlib.sha256(s.encode()).hexdigest()

def merkle_tree(leaves):
    if not leaves:
        raise SystemExit("FAIL: no leaves")
    tree=[leaves[:]]
    while len(tree[-1]) > 1:
        layer=tree[-1]
        nxt=[]
        for i in range(0,len(layer),2):
            left=layer[i]
            right=layer[i+1] if i+1 < len(layer) else layer[i]
            nxt.append(h(left+right))
        tree.append(nxt)
    return tree

def proof_for(tree, idx):
    proof=[]
    for layer in tree[:-1]:
        if idx % 2 == 0:
            sib = idx + 1
            side = "right"
        else:
            sib = idx - 1
            side = "left"
        if sib < len(layer):
            proof.append({"side":side,"hash":"0x"+layer[sib]})
        idx //= 2
    return proof

manifest=json.loads(Path("creator-manifest.json").read_text())
artifacts=manifest["artifacts"]
leaves=[h(canon({"path":a["path"],"sha256":a["sha256"]})) for a in artifacts]
tree=merkle_tree(leaves)
creator_root="0x"+tree[-1][0]

global_leaf=json.loads(Path("global-leaves/jaywisdom.json").read_text())
if global_leaf["creator_root"] != creator_root:
    raise SystemExit(f"FAIL: root mismatch {creator_root} != {global_leaf['creator_root']}")

out=Path("artifact-proofs")
out.mkdir(exist_ok=True)

for i,a in enumerate(artifacts):
    leaf_hash="0x"+leaves[i]
    safe=re.sub(r"[^A-Za-z0-9._-]+","_",a["path"]).strip("_")
    obj={
        "schema":"artifact_merkle_proof_v1",
        "creator_id":"jaywisdom",
        "round":"015",
        "path":a["path"],
        "sha256":a["sha256"],
        "leaf_hash":leaf_hash,
        "proof":proof_for(tree,i),
        "creator_root":creator_root,
        "algorithm":"sha256",
        "authority":False
    }
    (out / f"{safe}.json").write_text(canon(obj)+"\n")

print("Loaded",len(artifacts),"entries")
print("Creator root matches global-leaves/jaywisdom.json")
print("Generated",len(artifacts),"artifact proofs")
print("creator_root",creator_root)
