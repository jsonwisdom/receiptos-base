#!/usr/bin/env python3
import argparse, json, hashlib, sys

ALG = "sha256-merkle-v1"

def strip0x(x):
    return x[2:] if isinstance(x, str) and x.startswith("0x") else x

def with0x(x):
    return x if isinstance(x, str) and x.startswith("0x") else "0x" + x

def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"))

def hhex(a, b):
    return "0x" + hashlib.sha256((strip0x(a) + strip0x(b)).encode()).hexdigest()

def rec(status, path=None, creator_root=None, computed_root=None, reason=None):
    r = {
        "status": status,
        "artifact_id": path,
        "creator_root": creator_root,
        "computed_root": computed_root,
        "algorithm": ALG,
        "authority": False
    }
    if status == "FAIL":
        r["reason"] = reason
    return {k: v for k, v in r.items() if v is not None}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proof", required=True)
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()

    path = creator_root = cur = None

    try:
        p = json.load(open(args.proof))
        for k in ["path", "leaf_hash", "proof", "creator_root"]:
            if k not in p:
                raise ValueError(f"missing required field: {k}")

        path = p["path"]
        creator_root = with0x(p["creator_root"])
        cur = with0x(p["leaf_hash"])

        if not isinstance(p["proof"], list):
            raise ValueError("modified proof path")

        for step in p["proof"]:
            if "hash" not in step or "side" not in step:
                raise ValueError("modified proof path")

            sibling = with0x(step["hash"])
            side = step["side"]

            if side == "left":
                cur = hhex(sibling, cur)
            elif side == "right":
                cur = hhex(cur, sibling)
            else:
                raise ValueError("modified proof path")

        status = "PASS" if cur.lower() == creator_root.lower() else "FAIL"
        out = rec(status, path, creator_root, cur, None if status == "PASS" else "root mismatch")

    except Exception as e:
        out = rec("FAIL", path, creator_root, cur, str(e))

    print(json.dumps(out, indent=2, sort_keys=True) if args.pretty else canon(out))
    return 0 if out["status"] == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())
