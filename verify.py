#!/usr/bin/env python3
import json, hashlib, sys
from pathlib import Path

def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def h(s):
    return hashlib.sha256(s.encode()).hexdigest()

def strip0x(x):
    return x[2:] if isinstance(x, str) and x.startswith("0x") else x

def verify(proof):
    if proof.get("authority") is not False:
        return False, "authority must be false"

    leaf_obj = {"path": proof["path"], "sha256": proof["sha256"]}
    leaf_hash = "0x" + h(canon(leaf_obj))

    if leaf_hash != proof["leaf_hash"]:
        return False, "leaf_hash mismatch"

    cur = strip0x(leaf_hash)

    for step in proof["proof"]:
        sib = strip0x(step["hash"])
        side = step["side"]
        if side == "left":
            cur = h(sib + cur)
        elif side == "right":
            cur = h(cur + sib)
        else:
            return False, "bad proof side"

    root = "0x" + cur
    if root != proof["creator_root"]:
        return False, "creator_root mismatch"

    return True, "intact"

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 verify.py artifact-proofs/<proof>.json")
        sys.exit(2)

    proof = json.loads(Path(sys.argv[1]).read_text())
    ok, status = verify(proof)

    receipt = {
        "schema": "GoblinCourtVerificationReceiptV1",
        "proof_file": sys.argv[1],
        "path": proof.get("path"),
        "leaf_hash": proof.get("leaf_hash"),
        "creator_root": proof.get("creator_root"),
        "authority": False,
        "invariant_status": status
    }
    receipt["receipt_hash"] = "0x" + h(canon(receipt))

    print(canon(receipt))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
