from __future__ import annotations

from pathlib import Path

import pytest

from receiptos.core.cloud_commands import is_allowed_gcloud_command as core_is_allowed
from receiptos.gcp.allowlist import command_path
from receiptos.gcp.allowlist import is_allowed_gcloud_command as gcp_is_allowed
from receiptos.gcp.errors import (
    AuthorityViolationError,
    DisallowedCommandError,
    GCPPacketValidationError,
)
from receiptos.gcp.validator import validate_gcp_readonly_packet


VALID_PACKET = {
    "authority": False,
    "project_id": "jaywisdom-boardroom",
    "operator_identity": "manual-test",
    "command": [
        "gcloud",
        "compute",
        "instances",
        "list",
        "--format=json",
    ],
    "evidence": {
        "source": "manual-test",
        "observation": "empty instance list",
        "items": [],
    },
    "checksum": "sha256:test-placeholder",
    "observed_at": "2026-07-08T12:00:00Z",
    "classifications": [
        "GCP_READONLY_OBSERVATION",
    ],
}


def test_core_cloud_commands_wrapper_preserves_allowlist_behavior():
    command = [
        "gcloud",
        "compute",
        "instances",
        "list",
        "--format=json",
    ]

    assert core_is_allowed(command) is True
    assert gcp_is_allowed(command) is True
    assert core_is_allowed(command) == gcp_is_allowed(command)


def test_gcp_allowlist_accepts_known_readonly_command():
    assert gcp_is_allowed(
        [
            "gcloud",
            "compute",
            "instances",
            "list",
            "--format=json",
        ]
    ) is True


@pytest.mark.parametrize(
    "command",
    [
        [
            "gcloud",
            "compute",
            "instances",
            "create",
            "example-vm",
            "--format=json",
        ],
        [
            "gcloud",
            "compute",
            "instances",
            "delete",
            "example-vm",
            "--format=json",
        ],
        [
            "gcloud",
            "config",
            "set",
            "project",
            "example-project",
            "--format=json",
        ],
        [
            "gcloud",
            "auth",
            "login",
            "--format=json",
        ],
    ],
)
def test_gcp_allowlist_rejects_mutating_or_authorizing_commands(command):
    assert gcp_is_allowed(command) is False


@pytest.mark.parametrize(
    "command",
    [
        [
            "gcloud",
            "compute",
            "instances",
            "list",
        ],
        [
            "gcloud",
            "compute",
            "instances",
            "list",
            "--format=yaml",
        ],
        [
            "gcloud",
            "compute",
            "instances",
            "list",
            "--format",
            "json",
        ],
    ],
)
def test_gcp_allowlist_requires_json_format_flag(command):
    assert gcp_is_allowed(command) is False


@pytest.mark.parametrize(
    "command",
    [
        [
            "gcloud",
            "compute",
            "instances",
            "list",
            "--format=json",
            ";",
        ],
        [
            "gcloud",
            "compute",
            "instances",
            "list",
            "--format=json",
            "|",
        ],
        [
            "gcloud",
            "compute",
            "instances",
            "list",
            "--format=json",
            "$(whoami)",
        ],
        [
            "gcloud",
            "compute",
            "instances",
            "list",
            "--format=json",
            ">",
        ],
    ],
)
def test_gcp_allowlist_rejects_shell_fragments(command):
    assert gcp_is_allowed(command) is False


@pytest.mark.parametrize(
    "command",
    [
        "",
        b"gcloud compute instances list --format=json",
        None,
        [],
        ["not-gcloud", "compute", "instances", "list", "--format=json"],
        ["gcloud"],
        ["gcloud", "--format=json"],
        ["gcloud", "compute", "instances", "list", "--format=json", 123],
    ],
)
def test_gcp_allowlist_malformed_inputs_fail_closed(command):
    assert gcp_is_allowed(command) is False


def test_command_path_ignores_flags_and_preserves_command_tokens():
    assert command_path(
        [
            "gcloud",
            "compute",
            "instances",
            "list",
            "--format=json",
            "--project",
            "jaywisdom-boardroom",
        ]
    ) == (
        "compute",
        "instances",
        "list",
        "jaywisdom-boardroom",
    )


def test_validator_resolves_schema_outside_repo_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    assert validate_gcp_readonly_packet(dict(VALID_PACKET)) is True


def test_validator_rejects_non_mapping_packet():
    with pytest.raises(GCPPacketValidationError):
        validate_gcp_readonly_packet("not-a-packet")  # type: ignore[arg-type]


@pytest.mark.parametrize("authority", [None, "false", 0, 1, True])
def test_validator_rejects_non_literal_false_authority(authority):
    packet = dict(VALID_PACKET)
    packet["authority"] = authority

    with pytest.raises(AuthorityViolationError):
        validate_gcp_readonly_packet(packet)


def test_validator_rejects_missing_authority():
    packet = dict(VALID_PACKET)
    packet.pop("authority")

    with pytest.raises(AuthorityViolationError):
        validate_gcp_readonly_packet(packet)


def test_validator_rejects_non_string_command_tokens():
    packet = dict(VALID_PACKET)
    packet["command"] = [
        "gcloud",
        "compute",
        "instances",
        "list",
        "--format=json",
        123,
    ]

    with pytest.raises(GCPPacketValidationError):
        validate_gcp_readonly_packet(packet)


@pytest.mark.parametrize(
    "command",
    [
        "gcloud compute instances list --format=json",
        None,
        (),
        [],
    ],
)
def test_validator_rejects_missing_or_non_list_command(command):
    packet = dict(VALID_PACKET)
    packet["command"] = command

    with pytest.raises(DisallowedCommandError):
        validate_gcp_readonly_packet(packet)


def test_validator_rejects_mutating_command():
    packet = dict(VALID_PACKET)
    packet["command"] = [
        "gcloud",
        "compute",
        "instances",
        "create",
        "example-vm",
        "--format=json",
    ]

    with pytest.raises(DisallowedCommandError):
        validate_gcp_readonly_packet(packet)


def test_validator_rejects_shell_fragment_command():
    packet = dict(VALID_PACKET)
    packet["command"] = [
        "gcloud",
        "compute",
        "instances",
        "list",
        "--format=json",
        ";",
    ]

    with pytest.raises(DisallowedCommandError):
        validate_gcp_readonly_packet(packet)


def test_validator_rejects_schema_failure_after_membrane_checks():
    packet = dict(VALID_PACKET)
    packet.pop("project_id")

    with pytest.raises(GCPPacketValidationError):
        validate_gcp_readonly_packet(packet)


def test_validator_accepts_injected_schema_path(tmp_path):
    schema_path = tmp_path / "minimal_schema.json"
    schema_path.write_text(
        """
        {
          "type": "object",
          "required": ["authority", "command"],
          "properties": {
            "authority": {"const": false},
            "command": {
              "type": "array",
              "items": {"type": "string"}
            }
          }
        }
        """,
        encoding="utf-8",
    )

    assert validate_gcp_readonly_packet(
        {
            "authority": False,
            "command": [
                "gcloud",
                "compute",
                "instances",
                "list",
                "--format=json",
            ],
        },
        schema_path=schema_path,
    ) is True


def test_validator_rejects_missing_injected_schema_path(tmp_path):
    missing_schema = tmp_path / "missing_schema.json"

    with pytest.raises(GCPPacketValidationError):
        validate_gcp_readonly_packet(
            dict(VALID_PACKET),
            schema_path=missing_schema,
        )


def test_validator_rejects_invalid_injected_schema_json(tmp_path):
    invalid_schema = tmp_path / "invalid_schema.json"
    invalid_schema.write_text("{not-json", encoding="utf-8")

    with pytest.raises(GCPPacketValidationError):
        validate_gcp_readonly_packet(
            dict(VALID_PACKET),
            schema_path=invalid_schema,
        )
