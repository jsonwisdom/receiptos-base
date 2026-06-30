#!/usr/bin/env python3
"""
EXT-021 / EXT-022 TNTR witness mesh verifier.

Verifies that TNTR-CRO-001 multi-chain witness mesh stays bounded to
identical payload-hash agreement only. This verifier does not resolve TNTR,
does not infer market truth, and never elevates authority.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SPEC_PATH = ROOT / "mesh" / "tntr-cro-001-witness-mesh-spec.json"
WITNESSES_PATH = ROOT / "mesh" / "tntr-cro-001-witnesses.example.json"
RECEIPT_PATH = ROOT / "receipts" / "tntr-013-multichain-witness-mesh.json"

FORBIDDEN_PATTERNS = [
    r"\bresolve_truth\b",
    r"\bresolve_market\b",
    r"\bdeclare_yes\b",
    r"\bdeclare_no\b",
    r"\bauthority_true\b",
    r"\btruth_consensus\b",
    r"\bmarket_truth\b",
    r"\bmarket_outcome\b",
    r"\bverdict\b",
    r"\btribunal\b",
]

REQUIRED_SPEC_FIELDS = [
    "mesh_id",
    "cro_id",
    "payloadHash",
    "canonical_payload_cid",
    "source_attestation_uid",
    "source_tx_hash",
    "source_chain",
    "chains",
    "witnesses",
    "threshold",
    "agreementModel",
    "authority",
    "classification",
    "meshState",
]

REQUIRED_WITNESS_FIELDS = [
    "chain",
    "txHash",
    "uid",
    "schema",
    "attester",
    "payloadHash",
    "timestamp",
    "classification",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def strip_policy_lists(obj: Any) -> Any:
    """Remove explicit forbidden-policy declarations before scanning live claims."""
    if isinstance(obj, dict):
        return {
            key: strip_policy_lists(value)
            for key, value in obj.items()
            if key not in {"forbidden", "forbidden_actions", "forbidden_terms"}
        }
    if isinstance(obj, list):
        return [strip_policy_lists(value) for value in obj]
    return obj


def check_no_forbidden_text(name: str, obj: Any) -> None:
    text = json.dumps(strip_policy_lists(obj), sort_keys=True).lower()
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text):
            fail(f"{name} contains forbidden truth/tribunal language: {pattern}")


def main() -> int:
    print("🔍 EXT-021/022 TNTR Witness Mesh Verification")
    print("=" * 72)

    if not SPEC_PATH.exists():
        fail(f"missing spec: {SPEC_PATH}")
    print("1. Mesh spec exists: PASS")

    spec = load_json(SPEC_PATH)
    print("2. Mesh spec valid JSON: PASS")

    missing = [field for field in REQUIRED_SPEC_FIELDS if field not in spec]
    if missing:
        fail(f"spec missing required fields: {missing}")
    print("3. Required spec fields present: PASS")

    if spec["cro_id"] != "TNTR-CRO-001":
        fail("cro_id mismatch")
    print("4. cro_id == TNTR-CRO-001: PASS")

    if spec["agreementModel"] != "IDENTICAL_PAYLOAD_HASH":
        fail("agreementModel must be IDENTICAL_PAYLOAD_HASH")
    print("5. agreement model locked: PASS")

    if spec["authority"] is not False:
        fail("authority must be boolean false")
    print("6. authority=false: PASS")

    if spec.get("publication_role") != "provenance_only":
        fail("publication_role must be provenance_only")
    print("7. publication_role=provenance_only: PASS")

    if not isinstance(spec["threshold"], int) or spec["threshold"] < 1:
        fail("threshold must be positive integer")
    print("8. threshold valid: PASS")

    if not WITNESSES_PATH.exists():
        fail(f"missing witness set: {WITNESSES_PATH}")
    print("9. Witness example exists: PASS")

    witnesses = load_json(WITNESSES_PATH)
    if not isinstance(witnesses, list):
        fail("witness file must be a JSON array")
    print("10. Witness example valid JSON array: PASS")

    canonical_hash = spec["payloadHash"]
    matching_witnesses = []
    placeholder_witnesses = []

    for index, witness in enumerate(witnesses):
        missing_witness_fields = [field for field in REQUIRED_WITNESS_FIELDS if field not in witness]
        if missing_witness_fields:
            fail(f"witness {index} missing fields: {missing_witness_fields}")

        if witness["payloadHash"] != canonical_hash:
            fail(f"witness {index} payloadHash mismatch")

        if witness["classification"] != "MULTI_HUB_UNREACHABLE":
            fail(f"witness {index} classification mismatch")

        required_live_values = [str(witness.get(k, "")) for k in ("txHash", "uid", "attester")]
        if any(v == "[placeholder]" for v in required_live_values):
            placeholder_witnesses.append(witness["chain"])
        else:
            matching_witnesses.append(witness["chain"])

    print("11. Witness fields/hash/classification validate: PASS")

    if spec["source_chain"] not in [w["chain"] for w in witnesses]:
        fail("source chain witness missing")
    print("12. Source chain witness present: PASS")

    live_match_count = len(set(matching_witnesses))
    threshold_met = live_match_count >= spec["threshold"]

    if threshold_met:
        mesh_state = "QUERYABLE"
    elif live_match_count > 0:
        mesh_state = "PARTIAL_WITNESS"
    else:
        mesh_state = "UNVERIFIED"

    check_no_forbidden_text("spec", spec)
    check_no_forbidden_text("witnesses", witnesses)
    print("13. No forbidden truth escalation language: PASS")

    receipt = {
        "receipt_id": "TNTR-013-MULTICHAIN-WITNESS-MESH",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mesh_id": spec["mesh_id"],
        "cro_id": spec["cro_id"],
        "canonical_payload_hash": canonical_hash,
        "canonical_payload_cid": spec["canonical_payload_cid"],
        "agreementModel": spec["agreementModel"],
        "threshold": spec["threshold"],
        "live_matching_witness_count": live_match_count,
        "matching_witness_chains": sorted(set(matching_witnesses)),
        "placeholder_witness_chains": sorted(set(placeholder_witnesses)),
        "computed_mesh_state": mesh_state,
        "threshold_met": threshold_met,
        "authority": False,
        "publication_role": "provenance_only",
        "classification": "replay_only",
        "boundary_note": "QUERYABLE means threshold agreement over identical payload hash only; it does not mean true, resolved, or authoritative.",
        "source": {
            "chain": spec["source_chain"],
            "attestation_uid": spec["source_attestation_uid"],
            "tx_hash": spec["source_tx_hash"],
            "schema_uid": spec.get("source_schema_uid"),
        },
        "checks": {
            "spec_exists": True,
            "spec_valid_json": True,
            "required_fields_present": True,
            "cro_id_valid": True,
            "agreement_model_identical_payload_hash": True,
            "authority_false": True,
            "publication_role_provenance_only": True,
            "witness_hashes_match_canonical": True,
            "no_truth_escalation": True,
        },
    }

    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"14. Receipt emitted: PASS ({RECEIPT_PATH})")
    print("=" * 72)
    print(f"OVERALL: PASS — mesh_state={mesh_state}, threshold_met={threshold_met}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
