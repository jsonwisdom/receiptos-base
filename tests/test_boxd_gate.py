"""Run: python -m unittest discover -s tests -p test_boxd_gate.py"""
import hashlib, json, pathlib, struct, sys, tempfile, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from boxd_card_gate import audit, machine_remediation

class BoxDTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        d = pathlib.Path(self.tmp.name)
        self.image = d / "candidate.png"
        self.transcript = d / "transcript.txt"
        self.manifest = d / "card.json"
        self.transcript.write_text("DONALD TRUMP: That's a big crowd.", encoding="utf-8")

    def make(self, w, h, quote="That's a big crowd.", inspection=None):
        # Header-only fixture exercises the exact format/geometry boundary.
        self.image.write_bytes(b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", w, h))
        m = {"card_id":"BBP-001", "image_sha256":hashlib.sha256(self.image.read_bytes()).hexdigest(),
             "transcript_sha256":hashlib.sha256(self.transcript.read_bytes()).hexdigest(),
             "quote":quote, "audio_status":"UNVERIFIED",
             "independent_visual_inspection":inspection}
        self.manifest.write_text(json.dumps(m), encoding="utf-8")

    def test_ten_panel_sheet_must_fail(self):
        self.make(1536,1024)
        r=audit(self.image,self.manifest,self.transcript)
        self.assertEqual(r["verdict"],"FAIL")
        self.assertEqual(r["checks"]["ONE_PORTRAIT_CARD"],"FAIL")

    def test_invented_quote_must_fail(self):
        self.make(1086,1448,quote="I CAN FIX IT IN ONE DAY!")
        self.assertEqual(audit(self.image,self.manifest,self.transcript)["checks"]["EXACT_QUOTE"],"FAIL")

    def test_uninspected_portrait_must_hold(self):
        self.make(1086,1448)
        r=audit(self.image,self.manifest,self.transcript)
        self.assertEqual(r["verdict"],"HOLD")
        self.assertEqual(r["checks"]["COMPLETE_GRUBBY_BORDER"],"HOLD")

    def test_false_audio_verified_fails(self):
        self.make(1086,1448)
        m=json.loads(self.manifest.read_text());m["audio_status"]="VERIFIED_WITH_RECEIPT"
        self.manifest.write_text(json.dumps(m))
        self.assertEqual(audit(self.image,self.manifest,self.transcript)["checks"]["AUDIO_CLAIM"],"FAIL")
    def test_failure_produces_rule_based_machine_repair(self):
        self.make(1536,1024)
        r=audit(self.image,self.manifest,self.transcript)
        fix=r["remediation"]
        self.assertEqual(fix["policy_id"],"BOXD_CI_FIRST_CARD_RULES_V2")
        self.assertFalse(fix["human_triage_required"])
        self.assertEqual(fix["machine_action"],"RUN_MISSING_MACHINE_INSPECTION_OR_HOLD")
        self.assertIn("R001",[x["rule_id"] for x in fix["failed_rules"]])

    def test_retry_budget_holds_instead_of_burdening_human(self):
        fix=machine_remediation({"ONE_PORTRAIT_CARD":"FAIL"},attempts=3)
        self.assertEqual(fix["machine_action"],"RETRY_BUDGET_EXHAUSTED;HOLD_WITH_RECEIPTS")
        self.assertFalse(fix["human_triage_required"])

    def test_unknown_defect_proposes_rule_not_fake_pass(self):
        fix=machine_remediation({"NEW_DEFECT":"FAIL"})
        self.assertTrue(fix["machine_action"].startswith("PROPOSE_NEW_RULE"))
        self.assertIsNone(fix["failed_rules"][0]["rule_id"])

    def test_clean_gate_has_no_repairs(self):
        fix=machine_remediation({"ONE_PORTRAIT_CARD":"PASS"})
        self.assertEqual(fix["machine_action"],"ELIGIBLE_FOR_PROMOTION")
        self.assertEqual(fix["failed_rules"],[])

if __name__=="__main__":
    unittest.main()
