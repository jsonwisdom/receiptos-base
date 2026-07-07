import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "tools" / "verify_load_witness.py"
FIXTURE_DIR = ROOT / "fixtures" / "load_verification" / "placeholder_bundle"


def test_placeholder_bundle_is_not_a_valid_witness():
    result = subprocess.run(
        [
            sys.executable,
            str(VERIFY),
            "--witness",
            str(FIXTURE_DIR / "receipt.invalid.json"),
            "--transparency-log",
            str(FIXTURE_DIR / "test-log.invalid.json"),
            "--chain-head",
            str(FIXTURE_DIR / "chain_head.invalid.json"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode != 0
    assert "INVALID_WITNESS_SCHEMA" in result.stderr


def test_placeholder_signature_is_not_structured_ed25519():
    sig = (FIXTURE_DIR / "receipt.invalid.sig").read_text(encoding="utf-8")
    assert "placeholder" in sig
    assert "public_key" not in sig
    assert "signature" in sig
