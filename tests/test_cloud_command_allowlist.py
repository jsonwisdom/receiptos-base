import json
from pathlib import Path

import pytest

from receiptos.core.cloud_commands import is_allowed_gcloud_command


def test_allows_service_account_describe_with_json_format():
    cmd = [
        "gcloud",
        "iam",
        "service-accounts",
        "describe",
        "gpp-drive-uploader@jaywisdom-boardroom.iam.gserviceaccount.com",
        "--format=json",
    ]
    assert is_allowed_gcloud_command(cmd) is True


def test_allows_service_account_keys_list_with_json_format():
    cmd = [
        "gcloud",
        "iam",
        "service-accounts",
        "keys",
        "list",
        "--iam-account=gpp-drive-uploader@jaywisdom-boardroom.iam.gserviceaccount.com",
        "--format=json",
    ]
    assert is_allowed_gcloud_command(cmd) is True


def test_allows_project_iam_policy_read_with_json_format():
    cmd = ["gcloud", "projects", "get-iam-policy", "jaywisdom-boardroom", "--format=json"]
    assert is_allowed_gcloud_command(cmd) is True


def test_rejects_missing_json_format():
    cmd = ["gcloud", "compute", "instances", "list"]
    assert is_allowed_gcloud_command(cmd) is False


@pytest.mark.parametrize(
    "cmd",
    [
        ["gcloud", "auth", "login", "--format=json"],
        ["gcloud", "config", "set", "project", "my-project", "--format=json"],
        ["gcloud", "services", "enable", "compute.googleapis.com", "--format=json"],
        ["gcloud", "run", "deploy", "my-service", "--format=json"],
        ["gcloud", "iam", "service-accounts", "keys", "create", "key.json", "--format=json"],
        ["gcloud", "iam", "service-accounts", "keys", "delete", "KEY_ID", "--format=json"],
        ["gcloud", "iam", "service-accounts", "disable", "my-sa", "--format=json"],
        [
            "gcloud",
            "projects",
            "add-iam-policy-binding",
            "my-project",
            "--member=serviceAccount:foo@bar",
            "--role=roles/owner",
            "--format=json",
        ],
    ],
)
def test_rejects_mutating_auth_or_credential_commands(cmd):
    assert is_allowed_gcloud_command(cmd) is False


def test_fixture_receipt_has_authority_false_and_readonly_command():
    fixture_path = Path("tests/fixtures/gcp_readonly_audit_seed.json")
    data = json.loads(fixture_path.read_text(encoding="utf-8"))

    assert data.get("authority") is False

    cmd = data.get("command")
    assert isinstance(cmd, list)
    assert is_allowed_gcloud_command(cmd) is True
