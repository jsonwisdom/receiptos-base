#!/usr/bin/env python3
import argparse, base64, hashlib, json, sys
from typing import Any, Dict, List, Tuple

PASS="PASS"; FAIL="FAIL"; INDET="INDETERMINATE"

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def b64(s: str):
    try: return base64.b64decode(s, validate=True)
    except Exception: return None

def verdict(packet: Dict[str, Any]) -> Tuple[str,str,bool,List[str],List[str]]:
    warnings=[]; policy=[]; tainted=False

    if packet.get("packet_version") != "1.0":
        return INDET, "packet_version_mismatch", False, ["packet_version_mismatch"], policy

    raw_b64 = packet.get("raw_payload")
    if not isinstance(raw_b64, str):
        return INDET, "missing_raw_payload", False, ["missing_raw_payload"], policy

    raw = b64(raw_b64)
    if raw is None:
        return INDET, "raw_payload_decode_error", False, ["raw_payload_decode_error"], policy

    actual = sha256_bytes(raw)

    if packet.get("byte_length") != len(raw):
        return INDET, "byte_length_mismatch", False, ["byte_length_mismatch"], policy

    if packet.get("raw_payload_sha256") != actual:
        return FAIL, "raw_payload_sha256_mismatch", False, warnings, policy

    manifest = packet.get("manifest")
    if not isinstance(manifest, dict):
        return INDET, "missing_manifest", False, ["missing_manifest"], policy

    content = manifest.get("content")
    manifest_sha = manifest.get("manifest_sha256")
    if not isinstance(content, str) or not isinstance(manifest_sha, str):
        return INDET, "incomplete_manifest_hash_fields", False, ["incomplete_manifest_hash_fields"], policy

    if sha256_bytes(content.encode("utf-8")) != manifest_sha:
        return FAIL, "manifest_sha256_mismatch", False, warnings, policy

    collector = packet.get("collector_identity", {})
    if collector.get("contract_valid") is False:
        policy.append("collector_invalid")
        return FAIL, "collector_invalid", True, ["taint_propagation_enforced"], policy

    h = packet.get("hash_comparison_rules", {})
    expected = h.get("expected_hash")
    declared = h.get("recomputed_hash")

    if expected is None:
        return INDET, "missing_expected_hash", False, ["missing_expected_hash"], policy
    if declared is None:
        return INDET, "missing_recomputed_hash", False, ["recomputed_hash_absent"], policy

    if actual != expected:
        return FAIL, "hash_mismatch", False, ["hash_mismatch_detected"], policy
    if actual != declared:
        return FAIL, "declared_recomputed_hash_incorrect", False, ["declared_recomputed_hash_incorrect"], policy

    if packet.get("manifest_annotations", {}).get("conflict_marker"):
        return INDET, "manifest_conflict", False, ["manifest_conflict_detected"], policy

    return PASS, "hash_verified", False, warnings, policy

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fixture", required=True)
    args = p.parse_args()
    try:
        packet=json.load(open(args.fixture, encoding="utf-8"))
        v,r,t,w,pf=verdict(packet)
        out={"verdict":v,"reason":r,"tainted":t,"warnings":w,"policy_failures":pf,"observation_id":packet.get("observation_id")}
    except Exception as e:
        out={"verdict":INDET,"reason":"fixture_load_error","tainted":False,"warnings":[type(e).__name__],"policy_failures":[],"observation_id":None}
    print(json.dumps(out, indent=2, sort_keys=True))
    sys.exit(0)

if __name__ == "__main__":
    main()
