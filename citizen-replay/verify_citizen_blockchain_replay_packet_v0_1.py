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
    assert src["commit_sha"] == "389a148dbe7e86f97572fa1c2ddc2198c7acc59f"
    assert src["github_blob_sha"] == "d5f1b35b159623aff66aef2c9e412109b736e718"
    exp = d["expected_primary_state"]
    assert exp["round_06_executive_state"] == "READY_NOT_ROLLED"
    assert exp["entry_terminal"] == "HOLD"
    assert exp["independent_chain_replay"] == "HOLD"
    assert exp["authority_created"] is False
    b = d["boundaries"]
    assert b["primary_ledger_not_replay_copy"] is True
    assert b["family_lane_imported"] is False
    assert b["authority_created"] is False
    assert d["replay_state"] == "HOLD_EXTERNAL_CHAIN_REPLAY_NOT_PERFORMED"
    print("RECEIPTOS_CITIZEN_REPLAY_PACKET=PASS_STRUCTURE")
    print("EXTERNAL_CHAIN_REPLAY=HOLD_NOT_PERFORMED")
    print("PRIMARY_LEDGER=COMPUTERWISDOM")
    print("ROUND_06_EXECUTIVE=READY_NOT_ROLLED")
    print("AUTHORITY_CREATED=FALSE")


if __name__ == "__main__":
    main()
