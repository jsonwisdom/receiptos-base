#!/usr/bin/env python3
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
P = HERE / "CITIZEN_BLOCKCHAIN_REPLAY_PACKET_V0_1.json"
ZERO = "0x" + "0" * 64


def main():
    d = json.loads(P.read_text())
    assert d["schema"] == "receiptos_citizen_blockchain_replay_packet.v0_1"
    assert d["packet_id"] == "CITIZEN_BLOCKCHAIN_REPLAY_PACKET_V0_1"

    src = d["primary_ledger"]
    assert src["repository"] == "jsonwisdom/COMPUTERWISDOM"
    assert src["commit_sha"] == "a0d30740c4e8e8844ad5e2fa304bc668a7ae3407"
    assert src["direct_replay_receipt_path"].endswith("CITIZEN_LEDGER_ITEM_001_EAS_UID_DIRECT_REPLAY_2026_08_18.json")

    exp = d["expected_primary_state"]
    assert exp["round_06_executive_state"] == "READY_NOT_ROLLED"
    assert exp["entry_terminal"] == "CONFLICT"
    assert exp["preserve_parent_conflict"] is True
    assert exp["child_recovery_terminal"] == "REJECT"
    assert exp["active_recovery_path"] == "OPTION_B_DIRECT_EAS_UID_REPLAY"
    assert exp["option_b_eas_uid_replay"] == "COMPLETED_REJECT_DECLARED_BASE_SEPOLIA_OBJECTS"
    assert exp["declared_transaction_edge"] == "REJECT"
    assert exp["declared_onchain_attestation_edge"] == "REJECT"
    assert exp["declared_schema_registration_edge"] == "REJECT"
    assert exp["authority_created"] is False

    bound = d["bound_replay"]
    assert bound["workflow_run_id"] == 32106944392
    assert bound["head_sha"] == "141d4af42578d28586ddcadbf661efcc33c7c0c2"
    assert bound["chain_id"] == 84532
    assert bound["transaction_result"] is None
    assert bound["transaction_receipt_result"] is None
    assert bound["easscan_attestation_result"] is None
    assert bound["eas_contract_uid_result"] == ZERO
    assert bound["schema_registry_uid_result"] == ZERO

    b = d["boundaries"]
    assert b["primary_ledger_not_replay_copy"] is True
    assert b["parent_conflict_not_rewritten"] is True
    assert b["negative_chain_replay_not_motive_proof"] is True
    assert b["rejected_base_sepolia_edge_not_global_absence"] is True
    assert b["family_lane_imported"] is False
    assert b["round_06_executive_advanced"] is False
    assert b["authority_created"] is False

    assert d["replay_state"] == "PARENT_CONFLICT_PRESERVED_CHILD_EAS_REPLAY_REJECT"

    print("RECEIPTOS_CITIZEN_REPLAY_PACKET=PASS_STRUCTURE")
    print("PRIMARY_LEDGER_TERMINAL=CONFLICT_PRESERVED")
    print("CHILD_EAS_RECOVERY=REJECT_DECLARED_BASE_SEPOLIA_OBJECTS")
    print("ROUND_06_EXECUTIVE=READY_NOT_ROLLED")
    print("AUTHORITY_CREATED=FALSE")


if __name__ == "__main__":
    main()
