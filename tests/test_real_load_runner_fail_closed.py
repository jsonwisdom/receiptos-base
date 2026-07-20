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


def metrics_command(qps=200, success_rate=1.0):
    payload = json.dumps({
        "observed_qps": qps,
        "latency_p95_ms": 25,
        "replay_success_rate": success_rate,
        "resource_usage": {"cpu_pct": 1},
    })
    return f"{sys.executable} -c 'print({payload!r})'"


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


def test_unauthorized_target_fails_closed(tmp_path):
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
    assert data["failed_conditions"] == ["replay_target_not_authorized"]


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


def test_authorized_local_command_can_emit_load_candidate(tmp_path):
    out = tmp_path / "result.json"
    result = run_runner(
        "--transform-version", "v0.1.0",
        "--target-qps", "200",
        "--duration-min", "15",
        "--replay-target", "authorized-local-replay",
        "--telemetry-sink", "local-log",
        "--command", metrics_command(),
        "--out", str(out),
    )
    assert result.returncode == 0
    data = json.loads(out.read_text())
    assert data["status"] == "LOAD_CANDIDATE"
    assert data["failed_conditions"] == []
    assert data["authority"] is False
    assert data["no_fake_green"] is True
    assert data["metrics"]["observed_qps"] == 200
    assert data["metrics"]["replay_success_rate"] == 1.0


def test_authorized_local_command_fails_closed_on_low_qps(tmp_path):
    out = tmp_path / "result.json"
    result = run_runner(
        "--transform-version", "v0.1.0",
        "--target-qps", "200",
        "--duration-min", "15",
        "--replay-target", "authorized-local-replay",
        "--telemetry-sink", "local-log",
        "--command", metrics_command(qps=199),
        "--out", str(out),
    )
    assert result.returncode == 2
    data = json.loads(out.read_text())
    assert data["status"] == "GOVERNANCE_GAP"
    assert "observed_qps_below_threshold" in data["failed_conditions"]
