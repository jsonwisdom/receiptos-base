#!/usr/bin/env python3
"""Run the Jay GitHub Garbage Pail Kids Factory disposable test lane.

This runner is intentionally conservative:
- reads only test fixture + agent specs
- writes only agents/gpk-factory/outbox/gpk-card-test-001/
- never writes canon/
- never writes quarantine/
- keeps authority=false
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CARD_ID = "gpk-card-test-001"
CARD_PATH = ROOT / "tests" / "fixtures" / "gpk-factory" / f"{CARD_ID}.json"
SCHEMA_PATH = ROOT / "schemas" / "receipt_card_v0.2.json"
MANIFEST_PATH = ROOT / "agents" / "gpk-factory" / "manifest.json"
OUTBOX = ROOT / "agents" / "gpk-factory" / "outbox" / CARD_ID

REQUIRED_CARD_FIELDS = [
    "receipt_id",
    "version",
    "series",
    "card_number",
    "title",
    "ticker",
    "description",
    "evidence",
    "birth_witness",
    "custody",
    "classifications",
    "identity_anchor",
    "authority",
    "core_hash",
    "cid",
]

HASH_RE = re.compile(r"^(sha256:)?[0-9a-fA-F]{64}$")
EAS_RE = re.compile(r"^0x[0-9a-fA-F]{64}$")
CID_RE = re.compile(r"^(Qm[1-9A-HJ-NP-Za-km-z]{44}|b[a-z2-7]{20,})$")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def fail(reason: str) -> None:
    OUTBOX.mkdir(parents=True, exist_ok=True)
    payload = {
        "artifact_type": "GPK_FACTORY_TEST_FAIL",
        "card_id": CARD_ID,
        "reason": reason,
        "authority": False,
    }
    write_json(OUTBOX / "factory_fail.json", payload)
    raise SystemExit(reason)


def validate_card(card: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_CARD_FIELDS if field not in card]
    if missing:
        fail("missing required card fields: " + ", ".join(missing))
    if card.get("authority") is not False:
        fail("authority must be false")
    if card.get("version") != "0.2.0":
        fail("version must be 0.2.0")
    if not HASH_RE.match(card["receipt_id"]):
        fail("receipt_id must be sha256 hash")
    if not HASH_RE.match(card["core_hash"]):
        fail("core_hash must be sha256 hash")
    if not CID_RE.match(card["cid"]):
        fail("cid does not match expected CID pattern")

    evidence = card["evidence"]
    for field in ["eas_uid", "ipfs_cid", "anchor_chain", "observed_at", "pinned_at"]:
        if not evidence.get(field):
            fail(f"evidence.{field} is required")
    if not EAS_RE.match(evidence["eas_uid"]):
        fail("evidence.eas_uid must be 0x + 64 hex")
    if not CID_RE.match(evidence["ipfs_cid"]):
        fail("evidence.ipfs_cid does not match expected CID pattern")

    custody = card["custody"]
    if custody.get("current_state") != "EVIDENCE_REVIEW":
        fail("test card must stay in EVIDENCE_REVIEW")
    if card.get("replay_status", {}).get("real_canon_touched") is not False:
        fail("test card must declare real_canon_touched=false")


def run_factory(card: dict[str, Any], manifest: dict[str, Any]) -> None:
    OUTBOX.mkdir(parents=True, exist_ok=True)

    evidence_packet = {
        "agent_id": "receipt-ricky",
        "artifact_type": "GPK_EVIDENCE_PACKET",
        "card_id": CARD_ID,
        "observation": card["description"],
        "claim_boundary": "Disposable test artifact only; not canon.",
        "evidence_anchor": str(CARD_PATH.relative_to(ROOT)),
        "source_timestamp": card["evidence"]["observed_at"],
        "intake_status": "READY_FOR_CANON_REVIEW",
        "authority": False,
    }
    evidence_packet["packet_hash"] = digest(evidence_packet)
    write_json(OUTBOX / "receipt-ricky" / "evidence_packet.json", evidence_packet)

    canon_report = {
        "agent_id": "canon-carrie",
        "artifact_type": "GPK_CANON_READINESS_REPORT",
        "card_id": CARD_ID,
        "schema_version": card["version"],
        "governance_contract_sha": digest(manifest),
        "receipt_hash": card["receipt_id"],
        "canon_hash": card["core_hash"],
        "readiness_status": "TEST_READY_NOT_CANON",
        "blocking_issues": [],
        "authority": False,
    }
    canon_report["report_hash"] = digest(canon_report)
    write_json(OUTBOX / "canon-carrie" / "canon_readiness_report.json", canon_report)

    lore_report = {
        "agent_id": "lore-larry",
        "artifact_type": "GPK_LORE_DRIFT_REPORT",
        "card_id": CARD_ID,
        "drift_status": "NO_DRIFT_DETECTED",
        "contradictions": [],
        "overclaims": [],
        "required_edits": [],
        "authority": False,
    }
    lore_report["report_hash"] = digest(lore_report)
    write_json(OUTBOX / "lore-larry" / "lore_drift_report.json", lore_report)

    release_packet = {
        "agent_id": "press-patty",
        "artifact_type": "GPK_RELEASE_PACKET",
        "card_id": CARD_ID,
        "character_name": "TESTY CHECKS",
        "title": card["title"],
        "short_caption": "Disposable factory test. Receipts only. No canon touched.",
        "release_notes": "Factory handoff test completed in non-canon lane.",
        "canon_hash": card["core_hash"],
        "evidence_anchor": str(CARD_PATH.relative_to(ROOT)),
        "release_status": "READY_FOR_HUMAN_REVIEW_TEST_ONLY",
        "authority": False,
    }
    release_packet["packet_hash"] = digest(release_packet)
    write_json(OUTBOX / "press-patty" / "release_packet.json", release_packet)

    summary = {
        "artifact_type": "GPK_FACTORY_TEST_SUMMARY",
        "card_id": CARD_ID,
        "agents_executed": [
            "receipt-ricky",
            "canon-carrie",
            "lore-larry",
            "press-patty",
        ],
        "correction_lane_executed": False,
        "canon_mutation": False,
        "real_canon_touched": False,
        "authority": False,
        "status": "GPK_FACTORY_TEST_PASS",
    }
    summary["summary_hash"] = digest(summary)
    write_json(OUTBOX / "factory_test_summary.json", summary)


def main() -> None:
    if not CARD_PATH.exists():
        fail(f"missing disposable test card: {CARD_PATH}")
    if not SCHEMA_PATH.exists():
        fail(f"missing schema: {SCHEMA_PATH}")
    if not MANIFEST_PATH.exists():
        fail(f"missing manifest: {MANIFEST_PATH}")

    card = read_json(CARD_PATH)
    manifest = read_json(MANIFEST_PATH)
    validate_card(card)
    run_factory(card, manifest)
    print("GPK factory test: PASS")
    print(f"outbox={OUTBOX.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
