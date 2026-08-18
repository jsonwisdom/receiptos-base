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
    assert src["commit_sha"] == "f9d738fe37d5222bdfea62661ddb263ccfda77d0"
    assert src["github_blob_sha"] == "a153c1ed91a2d0f73b8b86ebc2f8c18ea3e8bcda"
    assert src["negative_replay_receipt_path"].endswith("CITIZEN_LEDGER_ITEM_001_NEGATIVE_RPC_REPLAY_2026_08_18.json")

    exp = d["expected_primary_state"]
    assert exp["round_06_executive_state"] == "READY_NOT_ROLLED"
    assert exp["entry_terminal"] == "CONFLICT"
    assert exp["independent_chain_replay"] == "CONFLICT"
    assert exp["negative_replay_source"] == "USER_SUPPLIED_RPC_OUTPUT"
    assert exp["reject_threshold_met"] is False
    assert exp["authority_created"] is False

    b = d["boundaries"]
    assert b["primary_ledger_not_replay_copy"] is True
    assert b["tx_hash_not_fact"] is True
    assert b["repository_record_not_chain_truth"] is True
    assert b["family_lane_imported"] is False
    assert b["round_06_executive_advanced"] is False
    assert b["authority_created"] is False

    assert d["replay_state"] == "CONFLICT_NEGATIVE_RPC_REPLAY_BOUND_EXTERNAL_CONFIRMATION_OPEN"

    print("RECEIPTOS_CITIZEN_REPLAY_PACKET=PASS_STRUCTURE")
    print("PRIMARY_LEDGER_TERMINAL=CONFLICT")
    print("NEGATIVE_RPC_REPLAY=BOUND_USER_SUPPLIED")
    print("EXTERNAL_CONFIRMATION=OPEN")
    print("ROUND_06_EXECUTIVE=READY_NOT_ROLLED")
    print("AUTHORITY_CREATED=FALSE")


if __name__ == "__main__":
    main()
