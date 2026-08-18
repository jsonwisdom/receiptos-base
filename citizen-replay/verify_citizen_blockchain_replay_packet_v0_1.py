#!/usr/bin/env python3
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
P = HERE / "CITIZEN_BLOCKCHAIN_REPLAY_PACKET_V0_1.json"


def main():
    d = json.loads(P.read_text())
    assert d["schema"] == "receiptos_citizen_blockchain_replay_packet.v0_1"
    assert d["packet_id"] == "CITIZEN_BLOCKCHAIN_REPLAY_PACKET_V0_1"

    src = d["primary_ledger"]
    assert src["repository"] == "jsonwisdom/COMPUTERWISDOM"
    assert src["commit_sha"] == "f37fc371c68bb61232e4fc6bb53d522f31632880"
    assert src["github_blob_sha"] == "a153c1ed91a2d0f73b8b86ebc2f8c18ea3e8bcda"
    assert src["negative_replay_receipt_path"].endswith("CITIZEN_LEDGER_ITEM_001_NEGATIVE_RPC_REPLAY_2026_08_18.json")
    assert src["recovery_path"].endswith("EAS_UID_RECOVERY_REPLAY_V0_1.json")

    exp = d["expected_primary_state"]
    assert exp["round_06_executive_state"] == "READY_NOT_ROLLED"
    assert exp["entry_terminal"] == "CONFLICT"
    assert exp["independent_chain_replay"] == "CONFLICT"
    assert exp["preserve_parent_conflict"] is True
    assert exp["active_recovery_path"] == "OPTION_B_DIRECT_EAS_UID_REPLAY"
    assert exp["option_a_hash_correction"] == "BLOCKED_NO_CORRECTED_HASH"
    assert exp["negative_replay_source"] == "USER_SUPPLIED_RPC_OUTPUT"
    assert exp["reject_threshold_met"] is False
    assert exp["authority_created"] is False

    b = d["boundaries"]
    assert b["primary_ledger_not_replay_copy"] is True
    assert b["parent_conflict_not_rewritten"] is True
    assert b["tx_hash_not_fact"] is True
    assert b["repository_record_not_chain_truth"] is True
    assert b["uid_string_not_attestation"] is True
    assert b["search_absence_not_chain_absence"] is True
    assert b["family_lane_imported"] is False
    assert b["round_06_executive_advanced"] is False
    assert b["authority_created"] is False

    assert d["replay_state"] == "CONFLICT_PRESERVED_EAS_UID_RECOVERY_OPEN"

    print("RECEIPTOS_CITIZEN_REPLAY_PACKET=PASS_STRUCTURE")
    print("PRIMARY_LEDGER_TERMINAL=CONFLICT_PRESERVED")
    print("EAS_UID_RECOVERY=OPEN")
    print("OPTION_A_HASH_CORRECTION=BLOCKED_NO_CORRECTED_HASH")
    print("OPTION_B_DIRECT_EAS_UID_REPLAY=ACTIVE")
    print("ROUND_06_EXECUTIVE=READY_NOT_ROLLED")
    print("AUTHORITY_CREATED=FALSE")


if __name__ == "__main__":
    main()
