#!/usr/bin/env python3
"""Real load runner adapter v0.1.

This adapter is deliberately fail-closed. It does not sign receipts and it does
not promote LOAD_VERIFIED. Its only job is to produce candidate load evidence or
an explicit GOVERNANCE_GAP.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
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


def governance_gap(args: argparse.Namespace, failed_conditions: list[str]) -> RealLoadResult:
    metrics = {
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
        timestamp=dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
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
    return failures


def run_adapter(args: argparse.Namespace) -> RealLoadResult:
    failures = validate_args(args)
    if failures:
        return governance_gap(args, failures)

    # v0.1 does not execute external traffic. A later PR may connect this seam to
    # an authorized in-repo runner. Until then, fail closed rather than simulate.
    return governance_gap(args, ["authorized_real_runner_not_implemented"])


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
