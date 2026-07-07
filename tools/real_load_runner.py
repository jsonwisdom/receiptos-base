#!/usr/bin/env python3
"""Real load runner adapter v0.1.

This adapter is fail-closed. It does not sign receipts and it does not promote
LOAD_VERIFIED. Its job is to produce measured load evidence from an explicitly
authorized local command or return an explicit GOVERNANCE_GAP.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RealLoadResult:
    result_version: str
    status: str
    timestamp: str
    transform_version: str
    target_qps: int
    duration_min: int
    replay_target: str | None
    metrics: dict[str, Any]
    authority: bool
    no_fake_green: bool
    failed_conditions: list[str]
    output_hash: str


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(data: Any) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def governance_gap(args: argparse.Namespace, failed_conditions: list[str], metrics: dict[str, Any] | None = None) -> RealLoadResult:
    metrics = metrics or {
        "requested_target_qps": args.target_qps,
        "requested_duration_min": args.duration_min,
        "observed_qps": 0,
        "latency_p95_ms": None,
        "replay_success_rate": 0,
        "resource_usage": {},
    }
    base = {
        "transform_version": args.transform_version,
        "target_qps": args.target_qps,
        "duration_min": args.duration_min,
        "replay_target": args.replay_target,
        "metrics": metrics,
        "failed_conditions": failed_conditions,
    }
    return RealLoadResult(
        result_version="REAL_LOAD_RESULT_V0_1",
        status="GOVERNANCE_GAP",
        timestamp=timestamp(),
        transform_version=args.transform_version,
        target_qps=args.target_qps,
        duration_min=args.duration_min,
        replay_target=args.replay_target,
        metrics=metrics,
        authority=False,
        no_fake_green=True,
        failed_conditions=failed_conditions,
        output_hash=sha256_hex(base),
    )


def load_candidate(args: argparse.Namespace, metrics: dict[str, Any]) -> RealLoadResult:
    base = {
        "transform_version": args.transform_version,
        "target_qps": args.target_qps,
        "duration_min": args.duration_min,
        "replay_target": args.replay_target,
        "metrics": metrics,
        "failed_conditions": [],
    }
    return RealLoadResult(
        result_version="REAL_LOAD_RESULT_V0_1",
        status="LOAD_CANDIDATE",
        timestamp=timestamp(),
        transform_version=args.transform_version,
        target_qps=args.target_qps,
        duration_min=args.duration_min,
        replay_target=args.replay_target,
        metrics=metrics,
        authority=False,
        no_fake_green=True,
        failed_conditions=[],
        output_hash=sha256_hex(base),
    )


def validate_args(args: argparse.Namespace) -> list[str]:
    failures: list[str] = []
    if args.transform_version != "v0.1.0":
        failures.append("transform_version_not_pinned")
    if args.target_qps < args.min_qps:
        failures.append("target_qps_below_threshold")
    if args.duration_min < 15:
        failures.append("duration_below_minimum")
    if not args.replay_target:
        failures.append("replay_target_missing")
    if not args.telemetry_sink:
        failures.append("telemetry_sink_missing")
    if args.replay_target and args.replay_target != "authorized-local-replay":
        failures.append("replay_target_not_authorized")
    if args.replay_target == "authorized-local-replay" and not args.command:
        failures.append("authorized_command_missing")
    return failures


def parse_metrics(stdout: str, args: argparse.Namespace) -> dict[str, Any]:
    parsed = json.loads(stdout)
    observed_qps = parsed.get("observed_qps")
    success_rate = parsed.get("replay_success_rate")
    latency_p95 = parsed.get("latency_p95_ms")
    if not isinstance(observed_qps, (int, float)):
        raise ValueError("observed_qps_missing")
    if not isinstance(success_rate, (int, float)):
        raise ValueError("replay_success_rate_missing")
    if not isinstance(latency_p95, (int, float)):
        raise ValueError("latency_p95_ms_missing")
    return {
        "requested_target_qps": args.target_qps,
        "requested_duration_min": args.duration_min,
        "observed_qps": observed_qps,
        "latency_p95_ms": latency_p95,
        "replay_success_rate": success_rate,
        "resource_usage": parsed.get("resource_usage", {}),
        "command_stdout_sha256": hashlib.sha256(stdout.encode("utf-8")).hexdigest(),
    }


def run_authorized_command(args: argparse.Namespace) -> tuple[dict[str, Any], list[str]]:
    start = time.monotonic()
    proc = subprocess.run(
        args.command,
        shell=True,
        cwd=args.command_cwd,
        text=True,
        capture_output=True,
        timeout=args.timeout_sec,
    )
    elapsed = time.monotonic() - start
    failures: list[str] = []
    if proc.returncode != 0:
        failures.append("authorized_command_failed")
    try:
        metrics = parse_metrics(proc.stdout, args)
    except (json.JSONDecodeError, ValueError) as exc:
        metrics = {
            "requested_target_qps": args.target_qps,
            "requested_duration_min": args.duration_min,
            "observed_qps": 0,
            "latency_p95_ms": None,
            "replay_success_rate": 0,
            "resource_usage": {},
            "command_stdout_sha256": hashlib.sha256(proc.stdout.encode("utf-8")).hexdigest(),
            "parse_error": str(exc),
        }
        failures.append("authorized_command_metrics_invalid")
    metrics["command_elapsed_sec"] = round(elapsed, 6)
    metrics["command_stderr_sha256"] = hashlib.sha256(proc.stderr.encode("utf-8")).hexdigest()
    if metrics.get("observed_qps", 0) < args.min_qps:
        failures.append("observed_qps_below_threshold")
    if metrics.get("replay_success_rate", 0) < args.min_success_rate:
        failures.append("replay_success_rate_below_threshold")
    return metrics, failures


def run_adapter(args: argparse.Namespace) -> RealLoadResult:
    failures = validate_args(args)
    if failures:
        return governance_gap(args, failures)

    try:
        metrics, run_failures = run_authorized_command(args)
    except subprocess.TimeoutExpired:
        return governance_gap(args, ["authorized_command_timeout"])

    if run_failures:
        return governance_gap(args, run_failures, metrics)
    return load_candidate(args, metrics)


def write_result(path: Path, result: RealLoadResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run real load adapter fail-closed surface.")
    parser.add_argument("--transform-version", required=True)
    parser.add_argument("--target-qps", type=int, required=True)
    parser.add_argument("--duration-min", type=int, required=True)
    parser.add_argument("--replay-target")
    parser.add_argument("--telemetry-sink")
    parser.add_argument("--min-qps", type=int, default=200)
    parser.add_argument("--min-success-rate", type=float, default=1.0)
    parser.add_argument("--command")
    parser.add_argument("--command-cwd", default=".")
    parser.add_argument("--timeout-sec", type=int, default=60)
    parser.add_argument("--out", default="artifacts/real-load-result.json")
    parser.add_argument("--allow-governance-gap-exit-zero", action="store_true")
    args = parser.parse_args()

    result = run_adapter(args)
    write_result(Path(args.out), result)
    print(json.dumps(asdict(result), indent=2, sort_keys=True))

    if result.status == "LOAD_CANDIDATE":
        return 0
    return 0 if args.allow_governance_gap_exit_zero else 2


if __name__ == "__main__":
    raise SystemExit(main())
