#!/usr/bin/env python3
"""
Round 16 Artifact Validator
Cross-references replay_*.json artifacts against audit_validation.json.
Exit 0 on PASS, non-zero on mismatch.
"""

import json
import sys
import hashlib
import re
from pathlib import Path
from typing import Dict, Any, List


HEX64_RE = re.compile(r"^(0x)?[0-9a-fA-F]{64}$")
GIT_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def sha256_file(path: Path) -> str:
    """Compute SHA-256 of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contains_placeholder(value: Any) -> bool:
    """Reject obvious placeholder/summarized values."""
    if isinstance(value, str):
        lowered = value.lower()
        return (
            "..." in value
            or lowered in {"all", "match", "pass Δ0", "pass d0", "todo", "tbd", "placeholder"}
            or "full report above" in lowered
        )
    if isinstance(value, dict):
        return any(contains_placeholder(v) for v in value.values())
    if isinstance(value, list):
        return any(contains_placeholder(v) for v in value)
    return False


def validate_report(report: Dict[str, Any]) -> List[str]:
    """Validate replay_report.json fields."""
    errors = []
    required = ["receipt_count", "receipt_merkle_root", "ledger_state_root", "replay_divergence", "verdict"]
    for field in required:
        if field not in report:
            errors.append(f"Missing required field in report: {field}")

    if not isinstance(report.get("receipt_count"), int):
        errors.append("report.receipt_count must be an integer")

    if report.get("verdict") != "PASS":
        errors.append(f"report.verdict is {report.get('verdict')}, expected PASS")

    if report.get("replay_divergence") != 0:
        errors.append(f"report.replay_divergence is {report.get('replay_divergence')}, expected 0")

    for field in ["receipt_merkle_root", "ledger_state_root"]:
        value = report.get(field, "")
        if not isinstance(value, str) or not HEX64_RE.match(value):
            errors.append(f"report.{field} must be full 64-hex hash, optional 0x prefix: {value}")

    if contains_placeholder(report):
        errors.append("report contains placeholder or summarized values")

    return errors


def validate_manifest(manifest: Dict[str, Any]) -> List[str]:
    """Validate replay_manifest.json fields."""
    errors = []
    required = [
        "protocol_version",
        "manifest_version",
        "genesis_cid",
        "receipt_count",
        "receipt_merkle_root",
        "ledger_state_root",
        "integrity_seal",
        "git_commit_sha",
        "created_at",
        "signature",
    ]
    for field in required:
        if field not in manifest:
            errors.append(f"Missing required field in manifest: {field}")
        elif manifest[field] in [None, "", "0x0000000000000000000000000000000000000000"]:
            errors.append(f"Placeholder value for manifest.{field}: {manifest[field]}")

    if not isinstance(manifest.get("receipt_count"), int):
        errors.append("manifest.receipt_count must be an integer")

    for field in ["receipt_merkle_root", "ledger_state_root", "integrity_seal"]:
        value = manifest.get(field, "")
        if not isinstance(value, str) or not HEX64_RE.match(value):
            errors.append(f"manifest.{field} must be full 64-hex hash, optional 0x prefix: {value}")

    git_sha = manifest.get("git_commit_sha", "")
    if not isinstance(git_sha, str) or not GIT_SHA_RE.match(git_sha):
        errors.append(f"manifest.git_commit_sha must be a real 40-char Git commit SHA: {git_sha}")
    if git_sha == EMPTY_SHA256:
        errors.append("manifest.git_commit_sha is SHA-256 empty-content hash, not a Git commit SHA")

    if contains_placeholder(manifest):
        errors.append("manifest contains placeholder or summarized values")

    return errors


def validate_environment(env: Dict[str, Any]) -> List[str]:
    """Validate replay_environment.json fields."""
    errors = []
    required = ["protocol_version", "harness_version", "python_version", "os", "exit_code", "git_commit_sha"]
    for field in required:
        if field not in env:
            errors.append(f"Missing required field in environment: {field}")

    if env.get("exit_code") != 0:
        errors.append(f"environment.exit_code is {env.get('exit_code')}, expected 0")

    git_sha = env.get("git_commit_sha", "")
    if git_sha and (not isinstance(git_sha, str) or not GIT_SHA_RE.match(git_sha)):
        errors.append(f"environment.git_commit_sha must be a 40-char Git commit SHA: {git_sha}")
    if git_sha == EMPTY_SHA256:
        errors.append("environment.git_commit_sha is SHA-256 empty-content hash, not a Git commit SHA")

    if contains_placeholder(env):
        errors.append("environment contains placeholder or summarized values")

    return errors


def validate_stdout(stdout: str) -> List[str]:
    """Validate replay_stdout.txt contents."""
    errors = []
    lowered = stdout.lower()
    if "exit code 0" not in lowered and "exit_code=0" not in lowered and "exit_code: 0" not in lowered:
        errors.append("Exit code 0 not found in stdout")
    if "..." in stdout or "full report above" in lowered:
        errors.append("stdout contains placeholder or summarized transcript")
    if "final result" not in lowered and "validation passed" not in lowered and "deterministic" not in lowered:
        errors.append("stdout missing final replay verdict marker")
    return errors


def validate_audit(audit: Dict[str, Any]) -> List[str]:
    """Validate audit_validation.json fields."""
    errors = []
    if audit.get("verdict") not in {"PASS", "VALIDATION_PASSED"}:
        errors.append(f"audit.verdict is {audit.get('verdict')}, expected PASS")
    if contains_placeholder(audit):
        errors.append("audit_validation contains placeholder or summarized values")
    return errors


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    base = Path(".")
    errors: List[str] = []

    try:
        audit = load_json(base / "audit_validation.json")
        print("✅ audit_validation.json loaded")
    except Exception as e:
        print(f"❌ Failed to load audit_validation.json: {e}")
        return 1

    try:
        report = load_json(base / "replay_report.json")
        print("✅ replay_report.json loaded")
    except Exception as e:
        print(f"❌ Failed to load replay_report.json: {e}")
        return 1

    try:
        manifest = load_json(base / "replay_manifest.json")
        print("✅ replay_manifest.json loaded")
    except Exception as e:
        print(f"❌ Failed to load replay_manifest.json: {e}")
        return 1

    try:
        env = load_json(base / "replay_environment.json")
        print("✅ replay_environment.json loaded")
    except Exception as e:
        print(f"❌ Failed to load replay_environment.json: {e}")
        return 1

    try:
        stdout = (base / "replay_stdout.txt").read_text(encoding="utf-8")
        print("✅ replay_stdout.txt loaded")
    except Exception as e:
        print(f"❌ Failed to load replay_stdout.txt: {e}")
        return 1

    errors.extend(validate_audit(audit))
    errors.extend(validate_report(report))
    errors.extend(validate_manifest(manifest))
    errors.extend(validate_environment(env))
    errors.extend(validate_stdout(stdout))

    # Cross-reference checks.
    if report.get("receipt_count") != manifest.get("receipt_count"):
        errors.append(
            f"receipt_count mismatch: report={report.get('receipt_count')}, "
            f"manifest={manifest.get('receipt_count')}"
        )

    for field in ["receipt_merkle_root", "ledger_state_root"]:
        if report.get(field) != manifest.get(field):
            errors.append(
                f"{field} mismatch: report={report.get(field)}, manifest={manifest.get(field)}"
            )

    if env.get("git_commit_sha") and manifest.get("git_commit_sha") and env.get("git_commit_sha") != manifest.get("git_commit_sha"):
        errors.append(
            f"git_commit_sha mismatch: environment={env.get('git_commit_sha')}, "
            f"manifest={manifest.get('git_commit_sha')}"
        )

    if errors:
        print("\n❌ VALIDATION FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("\n✅ VALIDATION PASSED")
    print(f"  Receipt count: {report.get('receipt_count')}")
    print(f"  Divergence: {report.get('replay_divergence')}")
    print(f"  Verdict: {report.get('verdict')}")
    print(f"  Git commit: {manifest.get('git_commit_sha', '')[:8]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
