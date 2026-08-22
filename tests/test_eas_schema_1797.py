import json
import pathlib
import tempfile
import unittest

from ReplayBoard.eas_schema_1797 import (
    EAS_SCHEMA_UID,
    EVIDENCE_STATE,
    RETRIEVAL_STATE,
    ZERO_BYTES32,
    BridgeError,
    build_payload,
    parse_state,
    reject_floats,
)


class EASSchema1797BridgeTests(unittest.TestCase):
    def sample_receipt(self):
        return {
            "subject": "example-subject",
            "evidence_set_id": "EXAMPLE",
            "docket_id": 123,
            "invariants": {"authority": False},
        }

    def test_exact_eight_field_envelope(self):
        payload = build_payload(
            self.sample_receipt(),
            lineage_id="example-lineage",
            previous_receipt_hash=ZERO_BYTES32,
            authority_chain="COURTLISTENER",
            official_ref="example-ref",
            created_at=1,
            evidence_state=EVIDENCE_STATE["MATCH"],
            retrieval_state=RETRIEVAL_STATE["COMPLETE"],
            verified_artifacts=[],
        )
        self.assertEqual(payload["schema_uid"], EAS_SCHEMA_UID)
        self.assertEqual(
            list(payload["fields"].keys()),
            [
                "receipt_hash",
                "lineage_hash",
                "previous_receipt_hash",
                "subject_hash",
                "source_ref_hash",
                "created_at",
                "evidence_state",
                "retrieval_state",
            ],
        )
        self.assertEqual(payload["fields"]["previous_receipt_hash"], ZERO_BYTES32)
        self.assertEqual(payload["fields"]["evidence_state"], 2)
        self.assertEqual(payload["fields"]["retrieval_state"], 0)
        self.assertFalse(payload["authority_created"])
        self.assertTrue(payload["offline_only"])

    def test_unknown_enum_fails_closed(self):
        with self.assertRaises(BridgeError):
            parse_state("99", EVIDENCE_STATE, "evidence_state")
        with self.assertRaises(BridgeError):
            parse_state("BOGUS", RETRIEVAL_STATE, "retrieval_state")

    def test_float_rejected(self):
        with self.assertRaises(BridgeError):
            reject_floats({"bad": 1.5})

    def test_created_at_uint64_boundary(self):
        with self.assertRaises(BridgeError):
            build_payload(
                self.sample_receipt(),
                lineage_id="x",
                previous_receipt_hash=ZERO_BYTES32,
                authority_chain="COURTLISTENER",
                official_ref="x",
                created_at=-1,
                evidence_state=0,
                retrieval_state=0,
                verified_artifacts=[],
            )


if __name__ == "__main__":
    unittest.main()
