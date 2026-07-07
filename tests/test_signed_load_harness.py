import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "tools" / "load_harness.py"
VERIFY = ROOT / "tools" / "verify_load_witness.py"
TEST_HEAD = "675299ee0ceb6db36070e600ef599fccb4b14b30"


def test_harness_emits_signed_governance_gap_bundle(tmp_path):
    run_id = "signed-gap-test"
    env = os.environ.copy()
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
    assert result.returncode == 0

    receipt_path = tmp_path / "receipts" / f"{run_id}.json"
    sig_path = tmp_path / "receipts" / f"{run_id}.json.sig"
    log_path = tmp_path / "transparency" / "log" / f"log-{TEST_HEAD}.json"
    chain_head_path = tmp_path / "transparency" / "index" / "chain_head.json"

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

    verify = subprocess.run(
        [
            sys.executable,
            str(VERIFY),
            "--witness", str(receipt_path),
            "--transparency-log", str(log_path),
            "--chain-head", str(chain_head_path),
            "--allow-governance-gap-exit-zero",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert verify.returncode == 0
    verified = json.loads(verify.stdout)
    assert verified["status"] == "GOVERNANCE_GAP"
    assert verified["checks"]["signature_valid"] is True
    assert verified["checks"]["receipt_digest_match"] is True
    assert verified["checks"]["failed_conditions_empty"] is False
