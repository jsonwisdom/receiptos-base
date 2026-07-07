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
