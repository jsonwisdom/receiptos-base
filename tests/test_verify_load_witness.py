import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "tools" / "verify_load_witness.py"


def run_verify(witness: Path, log: Path, head: Path, *extra):
    return subprocess.run(
        [
            sys.executable,
            str(VERIFY),
            "--witness", str(witness),
            "--transparency-log", str(log),
            "--chain-head", str(head),
            *extra,
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def write(path: Path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def base_witness():
    return {
        "witness_version": "LOAD_VERIFICATION_WITNESS_V0_1",
        "run_id": "test-run",
        "transform_version": "v0.1.0",
        "target_qps": 200,
        "duration_min": 15,
        "gate_result": {
            "status": "GOVERNANCE_GAP",
            "timestamp": "2026-07-07T16:09:26Z",
            "checks_passed": 0,
            "drift_detected": False,
            "replay_surface": "AL → receiptos-base",
            "public_surface": "aligned",
        },
        "receipt_integrity": {
            "receipt_id": "gap-test",
            "receipt_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "jcs_canonical": True,
            "signature_verified": False,
        },
        "transparency_continuity": {
            "log_id": "log-test",
            "chain_head": "9842db06e5fabf3403a61872c1e2d33c3b233acc",
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
        "membrane_unchanged": False,
        "failed_conditions": ["signed_receipt_integrity_missing"],
    }


def test_governance_gap_result_can_exit_zero_when_allowed(tmp_path):
    witness = base_witness()
    log = {"run_id": "test-run", "status": "GOVERNANCE_GAP"}
    head = {
        "chain_head": "9842db06e5fabf3403a61872c1e2d33c3b233acc",
        "latest_run_id": "test-run",
        "latest_status": "GOVERNANCE_GAP",
    }
    wp = tmp_path / "witness.json"
    lp = tmp_path / "log.json"
    hp = tmp_path / "head.json"
    write(wp, witness)
    write(lp, log)
    write(hp, head)

    result = run_verify(wp, lp, hp, "--allow-governance-gap-exit-zero")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["status"] == "GOVERNANCE_GAP"
    assert data["checks"]["signature_valid"] is False


def test_schema_invalid_witness_rejected(tmp_path):
    wp = tmp_path / "bad.json"
    lp = tmp_path / "log.json"
    hp = tmp_path / "head.json"
    write(wp, {"gate_result": {"status": "LOAD_VERIFIED"}})
    write(lp, {})
    write(hp, {})
    result = run_verify(wp, lp, hp)
    assert result.returncode != 0
    assert "INVALID_WITNESS_SCHEMA" in result.stderr


def test_load_verified_requires_matching_digest(tmp_path):
    witness = base_witness()
    witness["gate_result"]["status"] = "LOAD_VERIFIED"
    witness["gate_result"]["checks_passed"] = 11
    witness["receipt_integrity"]["signature_verified"] = True
    witness["membrane_unchanged"] = True
    witness["failed_conditions"] = []
    log = {"run_id": "test-run", "status": "LOAD_VERIFIED"}
    head = {
        "chain_head": "9842db06e5fabf3403a61872c1e2d33c3b233acc",
        "latest_run_id": "test-run",
        "latest_status": "LOAD_VERIFIED",
    }
    wp = tmp_path / "witness.json"
    lp = tmp_path / "log.json"
    hp = tmp_path / "head.json"
    write(wp, witness)
    write(lp, log)
    write(hp, head)

    result = run_verify(wp, lp, hp, "--allow-governance-gap-exit-zero")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["status"] == "GOVERNANCE_GAP"
    assert data["checks"]["receipt_digest_match"] is False
