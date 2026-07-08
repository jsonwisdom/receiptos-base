import copy
import json
import os
from pathlib import Path

import pytest

from receiptos.core.gcp_validator import GCPPacketValidationError, validate_gcp_readonly_packet


FIXTURE_PATH = Path("tests/fixtures/gcp_readonly_audit_seed.json")


def load_fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_valid_packet_passes_validator():
    packet = load_fixture()

    assert validate_gcp_readonly_packet(packet) is True


def test_valid_packet_passes_validator_outside_repo_cwd(tmp_path):
    packet = load_fixture()
    previous_cwd = Path.cwd()

    try:
        os.chdir(tmp_path)
        assert validate_gcp_readonly_packet(packet) is True
    finally:
        os.chdir(previous_cwd)


def test_validator_rejects_authority_change():
    packet = load_fixture()
    packet["authority"] = True

    with pytest.raises(GCPPacketValidationError):
        validate_gcp_readonly_packet(packet)


def test_validator_rejects_raw_string_command():
    packet = load_fixture()
    packet["command"] = "not-tokenized"

    with pytest.raises(GCPPacketValidationError):
        validate_gcp_readonly_packet(packet)


def test_validator_rejects_non_string_command_tokens():
    packet = load_fixture()
    packet["command"] = ["gcloud", "compute", 123, "list", "--format=json"]

    with pytest.raises(GCPPacketValidationError, match="command tokens must be strings"):
        validate_gcp_readonly_packet(packet)


def test_validator_rejects_disallowed_command():
    packet = load_fixture()
    packet["command"] = ["gcloud", "unknown", "surface", "list", "--format=json"]

    with pytest.raises(GCPPacketValidationError):
        validate_gcp_readonly_packet(packet)


def test_validator_rejects_missing_required_schema_field():
    packet = load_fixture()
    packet.pop("checksum")

    with pytest.raises(GCPPacketValidationError):
        validate_gcp_readonly_packet(packet)


def test_validator_rejects_additional_properties():
    packet = load_fixture()
    packet["extra"] = "drift"

    with pytest.raises(GCPPacketValidationError):
        validate_gcp_readonly_packet(packet)


def test_validator_does_not_mutate_packet():
    packet = load_fixture()
    before = copy.deepcopy(packet)

    validate_gcp_readonly_packet(packet)

    assert packet == before
