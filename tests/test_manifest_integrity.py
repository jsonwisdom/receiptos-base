import subprocess
from pathlib import Path

import pytest

MANIFEST_TEST_MAP = {
    "valid/manifest.valid.json": 0,
    "invalid/tree_hash_mismatch.json": 4,
    "invalid/commit_unresolvable.json": 5,
    "invalid/missing_surface.json": 5,
}

@pytest.mark.parametrize("manifest_path, expected_code", MANIFEST_TEST_MAP.items())
def test_manifest_integrity_gates(manifest_path, expected_code):
    path = Path("manifests") / manifest_path
    result = subprocess.run(
        ["receiptos", "manifest", "verify", str(path)],
        capture_output=True,
        text=True
    )

    assert result.returncode == expected_code, (
        f"{manifest_path} expected exit {expected_code}, got {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )

def test_replay_run_accepts_valid_manifest():
    result = subprocess.run(
        ["receiptos", "replay", "run", "manifests/valid/manifest.valid.json"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert '"receipt_type": "replay_run"' in result.stdout
