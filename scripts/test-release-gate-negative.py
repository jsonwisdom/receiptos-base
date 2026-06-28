#!/usr/bin/env python3
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from jsonschema import Draft7Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "evidence-bundle.schema.json"
VERIFIER = ROOT / "scripts" / "verify-evidence-bundle.py"
TEMPLATE = ROOT / "evidence" / "ROS-0001" / "evidence-bundle.template.json"


def expect_exit_1(name: str, cmd: list[str]) -> None:
    result = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 1:
        print(f"negative test failed: {name} returned {result.returncode}, expected 1", file=sys.stderr)
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise SystemExit(1)
    print(f"negative test ok: {name} exited 1")


def schema_rejects_template() -> None:
    schema = json.loads(SCHEMA.read_text())
    bundle = json.loads(TEMPLATE.read_text())
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(bundle))
    if not errors:
        print("negative test failed: template passed schema", file=sys.stderr)
        raise SystemExit(1)
    print("negative test ok: placeholder template rejected by schema")


def verifier_rejects_template() -> None:
    expect_exit_1("verifier rejects placeholder template", [sys.executable, str(VERIFIER), str(TEMPLATE)])


def valid_shape() -> dict:
    return {
        "rosId": "ROS-0001",
        "version": "0.1.0",
        "artifact": {
            "name": "ReceiptOS Genesis Cover",
            "digest": "0" * 64,
            "size": 1
        },
        "publication": {
            "repository": "https://github.com/jsonwisdom/receiptos-base",
            "commit": "71071f5de28aa3561cc22feb658a15da5a03bf81",
            "tag": "v0.1.0",
            "timestamp": "2026-06-28T00:00:00Z"
        },
        "evidence": {
            "eas_uid": "0x" + "1" * 64,
            "chain": "base",
            "zora_coin": "0xd0c736467e0d496cc56209a36f28264b86c49582",
            "ipfs_cid": "bafybeigdyrztvalidshapeonly"
        },
        "signature": {
            "algorithm": "ed25519",
            "signer": "deployer",
            "key_id": "deployer.pub",
            "sig": "AAAA"
        },
        "verificationScript": {
            "path": "scripts/verify-evidence-bundle.py",
            "algorithm": "sha256",
            "digest": "0" * 64
        },
        "timestamp": "2026-06-28T00:00:00Z",
        "verifier": {
            "name": "receiptos-verifier",
            "version": "0.1.0",
            "commit": "71071f5de28aa3561cc22feb658a15da5a03bf81"
        },
        "metadata": {
            "authority": False
        }
    }


def verifier_rejects_invalid_crypto() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bad-crypto.json"
        path.write_text(json.dumps(valid_shape(), indent=2))
        expect_exit_1("verifier rejects invalid crypto", [sys.executable, str(VERIFIER), str(path)])


def canonical_payload_is_not_json() -> None:
    spec = importlib.util.spec_from_file_location("receiptos_verifier", VERIFIER)
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(verifier)

    bundle = valid_shape()
    pipe_payload = verifier.canonical_payload(bundle)
    expected_pipe = (
        f"{bundle['rosId']}|"
        f"{bundle['artifact']['digest']}|"
        f"{bundle['publication']['commit']}|"
        f"{bundle['evidence']['eas_uid']}"
    ).encode("utf-8")
    old_json_payload = json.dumps({
        "rosId": bundle["rosId"],
        "version": bundle["version"],
        "artifact": bundle["artifact"],
        "publication": bundle["publication"],
        "evidence": bundle["evidence"],
        "verificationScript": bundle["verificationScript"],
        "timestamp": bundle["timestamp"],
        "verifier": bundle["verifier"],
    }, sort_keys=True, separators=(",", ":")).encode("utf-8")

    if pipe_payload != expected_pipe:
        print("negative test failed: pipe payload mismatch", file=sys.stderr)
        raise SystemExit(1)
    if pipe_payload == old_json_payload:
        print("negative test failed: old JSON payload still accepted as canonical", file=sys.stderr)
        raise SystemExit(1)
    print("negative test ok: canonical payload is pipe, not JSON")


if __name__ == "__main__":
    schema_rejects_template()
    verifier_rejects_template()
    verifier_rejects_invalid_crypto()
    canonical_payload_is_not_json()
    print("negative release-gate tests passed")
