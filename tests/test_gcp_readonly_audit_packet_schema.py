import copy
import json
from pathlib import Path

import pytest
import jsonschema

from receiptos.core.cloud_commands import is_allowed_gcloud_command


SCHEMA_PATH = Path("schemas/gcp_readonly_audit_packet_v0.1.json")
FIXTURE_PATH = Path("tests/fixtures/gcp_readonly_audit_seed.json")


def load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_seed_validates_against_schema():
    schema = load_schema()
    packet = load_fixture()

    jsonschema.validate(instance=packet, schema=schema)

    assert packet["authority"] is False
    assert isinstance(packet["command"], list)
    assert is_allowed_gcloud_command(packet["command"]) is True


def test_schema_rejects_authority_change():
    schema = load_schema()
    packet = load_fixture()
    packet["authority"] = True

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=packet, schema=schema)


def test_schema_rejects_extra_fields():
    schema = load_schema()
    packet = load_fixture()
    packet["unexpected"] = "drift"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=packet, schema=schema)


def test_schema_rejects_missing_command():
    schema = load_schema()
    packet = load_fixture()
    packet.pop("command")

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=packet, schema=schema)


def test_schema_rejects_non_array_command():
    schema = load_schema()
    packet = load_fixture()
    packet["command"] = "not-tokenized"

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=packet, schema=schema)


def test_fixture_copy_is_stable_for_replay():
    packet = load_fixture()
    replay = copy.deepcopy(packet)

    assert packet == replay
