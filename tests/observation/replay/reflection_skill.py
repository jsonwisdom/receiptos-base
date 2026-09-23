#!/usr/bin/env python3
"""Instrument 010: deterministic, non-authoritative reflection over replay verdicts."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Dict, Iterable, List, Mapping

CANONICAL_REPLAY_CORE_SHA256 = "f9eb7daffc6bf16a52668716a0cf60c76c011b1a7dd55e695e3d56372a759c27"
ALLOWED_VERDICTS = {"PASS", "FAIL", "INDETERMINATE"}


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _normalize(item: Mapping[str, Any]) -> Dict[str, Any]:
    verdict = str(item.get("verdict", "INDETERMINATE"))
    if verdict not in ALLOWED_VERDICTS:
        verdict = "INDETERMINATE"

    warnings = item.get("warnings", [])
    policy_failures = item.get("policy_failures", [])

    return {
        "verdict": verdict,
        "reason": str(item.get("reason", "missing_reason")),
        "tainted": bool(item.get("tainted", False)),
        "warnings": sorted(str(value) for value in warnings if value is not None),
        "policy_failures": sorted(
            str(value) for value in policy_failures if value is not None
        ),
    }


def reflect_on_verdicts(verdicts: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    """Return an evidence-bound reflection receipt without creating authority."""

    normalized: List[Dict[str, Any]] = [_normalize(item) for item in verdicts]
    counts = Counter(item["verdict"] for item in normalized)
    reasons = Counter(item["reason"] for item in normalized)
    warning_counts = Counter(
        warning for item in normalized for warning in item["warnings"]
    )
    policy_counts = Counter(
        failure for item in normalized for failure in item["policy_failures"]
    )
    tainted_count = sum(1 for item in normalized if item["tainted"])
    sample_size = len(normalized)

    if sample_size == 0:
        epistemic_status = "NO_OBSERVATIONS"
        confidence = 0.0
        observation = "No verdict observations were supplied."
        recommended_next_action = "Provide replay verdict observations."
    else:
        epistemic_status = "OBSERVED_SAMPLE_ONLY"
        confidence = round(min(1.0, sample_size / 10.0), 3)
        observation = f"Reflected on {sample_size} supplied verdict observation(s)."
        recommended_next_action = (
            "Review failures, indeterminate outcomes, taint, and policy failures."
            if counts["FAIL"] or counts["INDETERMINATE"] or tainted_count
            else "Preserve the receipt and continue observation."
        )

    return {
        "instrument": "010",
        "instrument_name": "Reflection Skill",
        "creates_authority": False,
        "canonical_replay_core_sha256": CANONICAL_REPLAY_CORE_SHA256,
        "observation": observation,
        "epistemic_status": epistemic_status,
        "explicit_non_claim": (
            "This receipt summarizes only supplied observations and does not assert "
            "global existence, non-existence, truth, or execution authority."
        ),
        "confidence": confidence,
        "sample_size": sample_size,
        "verdict_counts": {
            "PASS": counts["PASS"],
            "FAIL": counts["FAIL"],
            "INDETERMINATE": counts["INDETERMINATE"],
        },
        "tainted_count": tainted_count,
        "reason_counts": dict(sorted(reasons.items())),
        "warning_counts": dict(sorted(warning_counts.items())),
        "policy_failure_counts": dict(sorted(policy_counts.items())),
        "recommended_next_action": recommended_next_action,
        "evidence_receipts": [
            {
                "index": index,
                "sha256": _sha256(item),
                "observation": item,
            }
            for index, item in enumerate(normalized)
        ],
        "batch_sha256": _sha256(normalized),
    }
