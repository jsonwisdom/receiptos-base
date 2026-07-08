from __future__ import annotations

from typing import Sequence


_ALLOWED_COMMAND_PATHS = {
    ("compute", "instances", "list"),
    ("compute", "disks", "list"),
    ("compute", "networks", "list"),
    ("iam", "service-accounts", "describe"),
    ("iam", "service-accounts", "keys", "list"),
    ("services", "list"),
    ("projects", "get-iam-policy"),
    ("projects", "describe"),
    ("run", "services", "list"),
    ("storage", "buckets", "describe"),
    ("storage", "buckets", "get-iam-policy"),
    ("asset", "search-all-resources"),
}

_BLOCKED_TOKENS = {
    "auth",
    "login",
    "config",
    "set",
    "create",
    "update",
    "remove",
    "enable",
    "disable",
    "deploy",
    "rotate",
    "add-iam-policy-binding",
    "remove-iam-policy-binding",
    "set-iam-policy",
}

_SHELL_CHARS = {";", "|", "&", ">", "<", "$", "(", ")"}


def _command_path(argv: list[str]) -> tuple[str, ...]:
    path = []
    for token in argv[1:]:
        if token.startswith("-"):
            continue
        path.append(token)
    return tuple(path)


def is_allowed_gcloud_command(argv: Sequence[str]) -> bool:
    if isinstance(argv, (str, bytes)):
        return False

    argv = list(argv)

    if not argv or argv[0] != "gcloud":
        return False

    if not any(arg == "--format=json" or arg.startswith("--format=json") for arg in argv):
        return False

    for token in argv:
        if any(char in token for char in _SHELL_CHARS):
            return False

    for token in argv[1:]:
        if token.lstrip("-") in _BLOCKED_TOKENS:
            return False

    path = _command_path(argv)
    return any(path[: len(allowed)] == allowed for allowed in _ALLOWED_COMMAND_PATHS)
