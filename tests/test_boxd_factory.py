"""Regression tests: production failures are owned by the machine, not operator."""
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"tools"))
from boxd_factory import run

class FactoryTests(unittest.TestCase):
    def test_missing_adapters_fail_closed_and_preserve_receipts(self):
        with tempfile.TemporaryDirectory() as td:
            d=pathlib.Path(td)
            transcript=d/"transcript.txt"
            transcript.write_text("Exact source quote",encoding="utf-8")
            report=run([{"card_id":"BBP-001","quote":"Exact source quote"}],
                       transcript,d/"out",max_attempts=3)
            self.assertEqual(report["release_status"],"HOLD")
            self.assertFalse(report["human_qc_required"])
            self.assertEqual(len(report["cards"][0]["attempts"]),3)
            self.assertFalse((d/"out"/"candidate_release.zip").exists())
            self.assertTrue((d/"out"/"factory_report.json").exists())
            self.assertTrue((d/"out"/"attempts"/"BBP-001"/"3"/"renderer.log").exists())

    def test_duplicate_ids_are_rejected_without_overwriting(self):
        with tempfile.TemporaryDirectory() as td:
            d=pathlib.Path(td)
            t=d/"source.txt"
            t.write_text("quote",encoding="utf-8")
            r=run([{"card_id":"BBP-001","quote":"quote"},
                   {"card_id":"BBP-001","quote":"quote"}],t,d/"out",max_attempts=1)
            self.assertEqual(r["cards"][1]["reason"],"INVALID_OR_DUPLICATE_ID")
            self.assertEqual(r["release_status"],"HOLD")

    def test_empty_input_cannot_pass(self):
        with tempfile.TemporaryDirectory() as td:
            d=pathlib.Path(td)
            t=d/"source.txt"
            t.write_text("quote")
            r=run([],t,d/"out")
            self.assertEqual(r["release_status"],"HOLD")
            self.assertEqual(r["passed"],0)

if __name__=="__main__":
    unittest.main()
