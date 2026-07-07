import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "tools" / "audit_load_witness.py"


def run_audit(path: Path):
    return subprocess.run(
        [sys.executable, str(AUDIT), str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def test_rejects_pass_string_placeholders():
    result = run_audit(ROOT / "fixtures" / "load_verification" / "pass_strings.invalid.json")
    assert result.returncode != 0
    assert "INVALID_SCHEMA" in result.stderr


def test_rejects_sentinel_hashes():
    result = run_audit(ROOT / "fixtures" / "load_verification" / "sentinel_hashes.invalid.json")
    assert result.returncode != 0
    assert "SENTINEL_RECEIPT_DIGEST" in result.stderr


def test_rejects_digest_mismatch_for_load_verified(tmp_path):
    witness = {
        "witness_version": "LOAD_VERIFICATION_WITNESS_V0_1",
        "run_id": "digest-mismatch",
        "transform_version": "v0.1.0",
        "target_qps": 200,
        "duration_min": 15,
        "gate_result": {
            "status": "LOAD_VERIFIED",
            "timestamp": "2026-07-07T15:45:26Z",
            "checks_passed": 11,
            "drift_detected": False,
            "replay_surface": "AL → receiptos-base",
            "public_surface": "aligned",
        },
        "receipt_integrity": {
            "receipt_id": "mismatch",
            "receipt_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "jcs_canonical": True,
            "signature_verified": True,
        },
        "signature": {
            "alg": "Ed25519",
            "public_key": "0000000000000000000000000000000000000000000000000000000000000000",
            "signature": "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        },
        "transparency_continuity": {
            "log_id": "log-digest-mismatch",
            "chain_head": "3ab6d83fb6ff9d34884c21fa0bf53969af7c8237",
            "merged_public_surface_sha": "1539e812a5784dc0719c5c8b883615c73255d4c3",
            "continuous_from": "1539e812a5784dc0719c5c8b883615c73255d4c3",
        },
        "transform_version_pinned": True,
        "doctrine_guards": {
            "authority_false": True,
            "no_fake_green": True,
            "no_synthetic_pass": True,
            "no_public_load_badge_before_witness": True,
        },
        "membrane_unchanged": True,
        "failed_conditions": [],
    }
    path = tmp_path / "digest_mismatch.json"
    path.write_text(json.dumps(witness), encoding="utf-8")
    result = run_audit(path)
    assert result.returncode != 0
    assert "RECEIPT_DIGEST_MISMATCH" in result.stderr
