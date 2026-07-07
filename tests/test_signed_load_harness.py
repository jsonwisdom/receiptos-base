import copy
import json
import os
import subprocess
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "tools" / "load_harness.py"
TEST_HEAD = "675299ee0ceb6db36070e600ef599fccb4b14b30"


def canonical_json(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def test_harness_emits_signed_governance_gap_bundle(tmp_path):
    run_id = "signed-gap-test"
    env = os.environ.copy()
    env.pop("GITHUB_SHA", None)
    env["CHAIN_HEAD"] = TEST_HEAD
    result = subprocess.run(
        [
            sys.executable,
            str(HARNESS),
            "--transform-version", "v0.1.0",
            "--target-qps", "200",
            "--duration-min", "15",
            "--run-id", run_id,
            "--allow-governance-gap-exit-zero",
        ],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr

    emitted = json.loads(result.stdout)
    receipt_path = tmp_path / emitted["receipt"]
    sig_path = tmp_path / emitted["signature"]
    log_path = tmp_path / emitted["transparency_log"]
    chain_head_path = tmp_path / emitted["chain_head"]

    assert receipt_path.exists()
    assert sig_path.exists()
    assert log_path.exists()
    assert chain_head_path.exists()

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    signature = sig_path.read_text(encoding="utf-8").strip()

    assert receipt["gate_result"]["status"] == "GOVERNANCE_GAP"
    assert receipt["receipt_integrity"]["signature_verified"] is True
    assert receipt["signature"]["alg"] == "Ed25519"
    assert receipt["signature"]["signature"] == signature
    assert "signed_receipt_integrity_missing" not in receipt["failed_conditions"]
    assert "real_load_runner_missing" in receipt["failed_conditions"]

    payload = copy.deepcopy(receipt)
    payload.pop("signature", None)
    public_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(receipt["signature"]["public_key"]))
    public_key.verify(bytes.fromhex(signature), canonical_json(payload).encode("utf-8"))
