from __future__ import annotations

import json
from dataclasses import asdict
from typing import Literal

from semantic_rendering import SemanticRenderResult, render_observer_result

SurfaceName = Literal["JSON", "CLI", "REPORT", "LOG"]
SURFACES: tuple[SurfaceName, ...] = ("JSON", "CLI", "REPORT", "LOG")


def _bounded_result(observer_result: str, *, wording: str = "Observer result: PROVEN") -> SemanticRenderResult:
    return render_observer_result(observer_result, wording=wording)


def render_json(observer_result: str, *, wording: str = "Observer result: PROVEN") -> str:
    result = _bounded_result(observer_result, wording=wording)
    return json.dumps(asdict(result), sort_keys=True, separators=(",", ":"))


def render_cli(observer_result: str, *, wording: str = "Observer result: PROVEN") -> str:
    result = _bounded_result(observer_result, wording=wording)
    return (
        f"{result.semantic_type} | {result.rendered_text} | "
        f"evidence_gate_proven={str(result.evidence_gate_proven).lower()} | "
        f"authority_created={str(result.authority_created).lower()}"
    )


def render_report(observer_result: str, *, wording: str = "Observer result: PROVEN") -> str:
    result = _bounded_result(observer_result, wording=wording)
    return (
        "## White House replay disposition\n"
        f"- semantic_type: `{result.semantic_type}`\n"
        f"- rendered_text: {result.rendered_text}\n"
        f"- evidence_gate_proven: {str(result.evidence_gate_proven).lower()}\n"
        f"- claim_proven: {str(result.claim_proven).lower()}\n"
        f"- fraud_proven: {str(result.fraud_proven).lower()}\n"
        f"- guilt_established: {str(result.guilt_established).lower()}\n"
        f"- legal_finding: {str(result.legal_finding).lower()}\n"
        f"- authority_created: {str(result.authority_created).lower()}\n"
    )


def render_log(observer_result: str, *, wording: str = "Observer result: PROVEN") -> str:
    result = _bounded_result(observer_result, wording=wording)
    return (
        "white_house_replay "
        f"semantic_type={result.semantic_type} "
        f"observer_result={result.observer_result} "
        f"rendered_text={result.rendered_text!r} "
        f"evidence_gate_proven={str(result.evidence_gate_proven).lower()} "
        f"claim_proven={str(result.claim_proven).lower()} "
        f"fraud_proven={str(result.fraud_proven).lower()} "
        f"guilt_established={str(result.guilt_established).lower()} "
        f"legal_finding={str(result.legal_finding).lower()} "
        f"authority_created={str(result.authority_created).lower()}"
    )


def render_surface(surface: SurfaceName, observer_result: str, *, wording: str = "Observer result: PROVEN") -> str:
    if surface == "JSON":
        return render_json(observer_result, wording=wording)
    if surface == "CLI":
        return render_cli(observer_result, wording=wording)
    if surface == "REPORT":
        return render_report(observer_result, wording=wording)
    if surface == "LOG":
        return render_log(observer_result, wording=wording)
    raise ValueError(f"unsupported surface: {surface}")
