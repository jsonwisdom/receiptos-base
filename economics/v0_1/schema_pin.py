"""Fail-closed vendored schema/spec pin verification for Agent Economics V0.1."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict

SOURCE_REPOSITORY = "jsonwisdom/AL"
SOURCE_BRANCH = "agent/jaywisdom-agent-economics-v0-1"
SOURCE_COMMIT = "af63889a692890cfd0e3ed74224b4feb1b614ac4"

# These are Git blob object IDs, not plain SHA-1(file_bytes).
EXPECTED_GIT_BLOB_SHA1 = {
    "JAYWISDOM_AGENT_ECONOMICS_V0_1.schema.json": "4ac089aa4824820634665f78a59b70e709c87292",
    "ECONOMIC_DECISION_RECEIPT_V0_1.schema.json": "0cf20aebc909b2f311868efdcf872b0f53af47ee",
    "REALIZED_ECONOMIC_OUTCOME_RECEIPT_V0_1.schema.json": "bedfcca08ea9c4aa73ca2f68510a65dd58cb5ad2",
    "JAYWISDOM_AGENT_ECONOMIC_GATE_V0_1.md": "ecd02c3b5f299c506b7638ef68f6b92b4f7a1b01",
}


class SchemaPinError(RuntimeError):
    """Raised when vendored truth-contract bytes are absent or drifted."""


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def verify_schema_pin(schema_dir: Path | None = None) -> Dict[str, Dict[str, str]]:
    """Verify exact vendored bytes against the AL Git blob IDs.

    Returns per-file Git blob SHA-1 and plain SHA-256 diagnostics. Any missing or
    drifted file raises SchemaPinError. This creates no execution authority.
    """
    root = schema_dir or (Path(__file__).resolve().parent / "schemas")
    report: Dict[str, Dict[str, str]] = {}
    errors = []

    for name, expected_blob in EXPECTED_GIT_BLOB_SHA1.items():
        path = root / name
        if not path.is_file():
            errors.append(f"MISSING:{name}")
            continue
        data = path.read_bytes()
        actual_blob = git_blob_sha1(data)
        sha256 = hashlib.sha256(data).hexdigest()
        report[name] = {"git_blob_sha1": actual_blob, "sha256": sha256}
        if actual_blob != expected_blob:
            errors.append(
                f"DRIFT:{name}:expected={expected_blob}:actual={actual_blob}"
            )

    if errors:
        raise SchemaPinError(";".join(errors))
    return report
