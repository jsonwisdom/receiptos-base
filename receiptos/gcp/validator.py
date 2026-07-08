from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema

from receiptos.core.authority import AuthorityViolation, enforce_authority
from receiptos.gcp.allowlist import is_allowed_gcloud_command
from receiptos.gcp.errors import AuthorityViolationError, DisallowedCommandError, SchemaValidationError


SCHEMA_PATH = Path("schemas/gcp_readonly_audit_packet_v0.1.json")


def load_schema(schema_path: Path = SCHEMA_PATH) -> dict[str, Any]:
    return json.loads(schema_path.read_text(encoding="utf-8"))


def validate_gcp_readonly_packet(packet: Mapping[str, Any], *, schema_path: Path = SCHEMA_PATH) -> bool:
    """Validate a Phase 2 GCP read-only packet without executing cloud commands."""
    if not isinstance(packet, Mapping):
        raise SchemaValidationError("packet must be a mapping")

    try:
        enforce_authority(packet.get("authority"))
    except AuthorityViolation as exc:
        raise AuthorityViolationError(str(exc)) from exc

    command = packet.get("command")
    if not isinstance(command, list):
        raise DisallowedCommandError("command must be a tokenized list")

    if not is_allowed_gcloud_command(command):
        raise DisallowedCommandError("command is not allowed by the GCP read-only membrane")

    schema = load_schema(schema_path)
    try:
        jsonschema.validate(instance=dict(packet), schema=schema)
    except jsonschema.ValidationError as exc:
        raise SchemaValidationError(f"schema validation failed: {exc.message}") from exc

    return True
