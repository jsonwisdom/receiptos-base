from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping

from receiptos.core.gcp_validator import GCPPacketValidationError, validate_gcp_readonly_packet


REQUIRED_RECEIPT_ANCHOR = "GRP-004-PROMO-20260708-6d405d9e"


class WeldValidationError(ValueError):
    pass


@dataclass(frozen=True)
class WeldResult:
    valid: bool
    output_hash: str
    receipt_anchor: str
    authority: bool


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_canonical(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise WeldValidationError(f"{field} must be a mapping")
    return value


def _verify_packet_digest(payload: Mapping[str, Any]) -> None:
    digest = payload.get("signature")
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        raise WeldValidationError("signature must be a sha256 digest")

    subject = dict(payload)
    subject.pop("signature", None)
    expected = sha256_canonical(subject)
    if digest != expected:
        raise WeldValidationError("signature mismatch")


def _verify_evidence_digest(cloud_observation: Mapping[str, Any]) -> None:
    checksum = cloud_observation.get("checksum")
    evidence = cloud_observation.get("evidence")
    if checksum != sha256_canonical(evidence):
        raise WeldValidationError("evidence checksum mismatch")


def validate_deerflow_weld(payload: Mapping[str, Any]) -> WeldResult:
    if not isinstance(payload, Mapping):
        raise WeldValidationError("payload must be a mapping")

    if payload.get("authority") is not False:
        raise WeldValidationError("authority must be false")

    receipt_anchor = payload.get("receipt_anchor")
    if receipt_anchor != REQUIRED_RECEIPT_ANCHOR:
        raise WeldValidationError("receipt_anchor mismatch")

    flow_definition = _require_mapping(payload.get("flow_definition"), "flow_definition")
    if flow_definition.get("harness") != "DeerFlow":
        raise WeldValidationError("unexpected harness")
    if flow_definition.get("receiptos_role") != "admissibility_gate":
        raise WeldValidationError("unexpected receiptos_role")

    cloud_observation = _require_mapping(payload.get("cloud_observation"), "cloud_observation")
    _verify_packet_digest(payload)
    _verify_evidence_digest(cloud_observation)

    try:
        validate_gcp_readonly_packet(cloud_observation)
    except GCPPacketValidationError as exc:
        raise WeldValidationError(str(exc)) from exc

    return WeldResult(
        valid=True,
        output_hash=sha256_canonical(payload),
        receipt_anchor=receipt_anchor,
        authority=False,
    )
