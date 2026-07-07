import json
import subprocess
from pathlib import Path

import pytest

RECEIPT_TEST_MAP = {
    "schema_validate.valid.json": 0,
    "valid/replay_run.valid.json": 0,
    "invalid/version_mismatch.json": 3,
    "invalid/authority_true.json": 3,
    "invalid/hash_mismatch.json": 4,
    "invalid/bad_invariant.json": 6,
}

def run_receiptos(path: Path, expected_code: int):
    if expected_code == 3:
        cmd = ["receiptos", "schema", "validate", str(path)]
    else:
        cmd = ["receiptos", "replay", "verify", str(path)]

    return subprocess.run(cmd, capture_output=True, text=True)

@pytest.mark.parametrize("receipt_path, expected_code", RECEIPT_TEST_MAP.items())
def test_receipt_integrity_gates(receipt_path, expected_code):
    path = Path("fixtures/receipts") / receipt_path
    result = run_receiptos(path, expected_code)

    assert result.returncode == expected_code, (
        f"{receipt_path} expected exit {expected_code}, "
        f"got {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


def test_replay_run_tree_hash_fail():
    """replay_run with tree_sha256 mismatch → exit 4, FAIL receipt"""
    result = subprocess.run(["receiptos", "replay", "run", "manifests/invalid/tree_hash_mismatch.json"],
                            capture_output=True, text=True)
    assert result.returncode == 4
    receipt = json.loads(result.stdout)
    assert receipt["status"] == "FAIL"
    assert receipt["exit_code"] == 4
    assert "INV_TREE_HASH_MATCH" in receipt["errors"][0]
    assert receipt["authority"] is False
    fixture = json.loads(Path("fixtures/receipts/invalid/replay_tree_hash_mismatch.json").read_text())
    assert receipt["receipt_type"] == fixture["receipt_type"]
    assert receipt["status"] == fixture["status"]

def test_replay_run_commit_unresolvable():
    """replay_run with bad commit_sha → exit 5, FAIL receipt"""
    result = subprocess.run(["receiptos", "replay", "run", "manifests/invalid/commit_unresolvable.json"],
                            capture_output=True, text=True)
    assert result.returncode == 5
    receipt = json.loads(result.stdout)
    assert receipt["status"] == "FAIL"
    assert receipt["exit_code"] == 5
    assert "INV_COMMIT_RESOLVABLE" in receipt["errors"][0]

def test_replay_run_missing_surface():
    """replay_run with missing canonical_surface → exit 5, FAIL receipt"""
    result = subprocess.run(["receiptos", "replay", "run", "manifests/invalid/missing_surface.json"],
                            capture_output=True, text=True)
    assert result.returncode == 5
    receipt = json.loads(result.stdout)
    assert receipt["status"] == "FAIL"
    assert receipt["exit_code"] == 5
    assert "INV_CANONICAL_SURFACES_PRESENT" in receipt["errors"][0]
