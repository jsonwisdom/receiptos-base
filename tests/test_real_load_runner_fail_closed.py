import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools" / "real_load_runner.py"


def run_runner(*args):
    return subprocess.run(
        [sys.executable, str(RUNNER), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def test_missing_replay_target_fails_closed(tmp_path):
    out = tmp_path / "result.json"
    result = run_runner(
        "--transform-version", "v0.1.0",
        "--target-qps", "200",
        "--duration-min", "15",
        "--telemetry-sink", "local-log",
        "--out", str(out),
    )
    assert result.returncode == 2
    data = json.loads(out.read_text())
    assert data["status"] == "GOVERNANCE_GAP"
    assert data["authority"] is False
    assert data["no_fake_green"] is True
    assert "replay_target_missing" in data["failed_conditions"]


def test_no_stub_candidate_even_with_inputs(tmp_path):
    out = tmp_path / "result.json"
    result = run_runner(
        "--transform-version", "v0.1.0",
        "--target-qps", "200",
        "--duration-min", "15",
        "--replay-target", "local-joy-rail",
        "--telemetry-sink", "local-log",
        "--out", str(out),
    )
    assert result.returncode == 2
    data = json.loads(out.read_text())
    assert data["status"] == "GOVERNANCE_GAP"
    assert data["failed_conditions"] == ["authorized_real_runner_not_implemented"]


def test_governance_gap_exit_zero_for_ci_probe(tmp_path):
    out = tmp_path / "result.json"
    result = run_runner(
        "--transform-version", "v0.1.0",
        "--target-qps", "200",
        "--duration-min", "15",
        "--replay-target", "local-joy-rail",
        "--telemetry-sink", "local-log",
        "--out", str(out),
        "--allow-governance-gap-exit-zero",
    )
    assert result.returncode == 0
    data = json.loads(out.read_text())
    assert data["status"] == "GOVERNANCE_GAP"
