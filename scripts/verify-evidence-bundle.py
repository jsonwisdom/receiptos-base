#!/usr/bin/env python3
import base64
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import requests
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
except Exception as exc:
    print(f"missing required verifier dependency: {exc}", file=sys.stderr)
    sys.exit(1)


def fail(message: str) -> None:
    print(f"release gate failed: {message}", file=sys.stderr)
    sys.exit(1)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_payload(bundle: dict) -> bytes:
    payload = {
        "rosId": bundle["rosId"],
        "version": bundle["version"],
        "artifact": bundle["artifact"],
        "publication": bundle["publication"],
        "evidence": bundle["evidence"],
        "verificationScript": bundle["verificationScript"],
        "timestamp": bundle["timestamp"],
        "verifier": bundle["verifier"],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def reject_placeholders(obj) -> None:
    if isinstance(obj, dict):
        for value in obj.values():
            reject_placeholders(value)
    elif isinstance(obj, list):
        for value in obj:
            reject_placeholders(value)
    elif isinstance(obj, str) and obj.startswith("REPLACE_WITH_"):
        fail(f"placeholder present: {obj}")


def verify_git_commit(commit: str) -> None:
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        fail("publication commit is not present in repository")


def verify_signature(bundle: dict) -> None:
    sig = bundle["signature"]
    key_path = Path("repo/keys") / sig["key_id"]
    if not key_path.exists():
        fail(f"missing public key: {key_path}")

    key_hex = key_path.read_text().strip()
    if key_hex.startswith("REPLACE_WITH_"):
        fail("deployer public key is placeholder")

    try:
        public_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(key_hex))
        signature = base64.b64decode(sig["sig"], validate=True)
        public_key.verify(signature, canonical_payload(bundle))
    except InvalidSignature:
        fail("invalid ed25519 signature")
    except Exception as exc:
        fail(f"signature verification error: {exc}")


def verify_eas_attestation(bundle: dict) -> None:
    eas_uid = bundle["evidence"]["eas_uid"]
    endpoint = os.environ.get("EAS_GRAPHQL_ENDPOINT", "https://base.easscan.org/graphql")
    query = """
    query Attestation($where: AttestationWhereUniqueInput!) {
      attestation(where: $where) {
        id
        txid
        revoked
      }
    }
    """
    try:
        response = requests.post(
            endpoint,
            json={"query": query, "variables": {"where": {"id": eas_uid}}},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        fail(f"EAS query failed: {exc}")

    attestation = data.get("data", {}).get("attestation")
    if not attestation:
        fail("EAS attestation not found")
    if attestation.get("revoked") is True:
        fail("EAS attestation is revoked")


def verify_bundle(bundle_path: str, artifact_path: str | None = None) -> None:
    bundle = json.loads(Path(bundle_path).read_text())
    reject_placeholders(bundle)

    if artifact_path:
        computed = sha256_file(Path(artifact_path))
        if computed != bundle["artifact"]["digest"]:
            fail("artifact digest mismatch")

    script_digest = sha256_file(Path(bundle["verificationScript"]["path"]))
    if script_digest != bundle["verificationScript"]["digest"]:
        fail("verification script digest mismatch")

    verify_git_commit(bundle["publication"]["commit"])
    verify_signature(bundle)
    verify_eas_attestation(bundle)

    print(f"verified {bundle['rosId']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: verify-evidence-bundle.py evidence-bundle.json [artifact]", file=sys.stderr)
        sys.exit(1)
    verify_bundle(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
