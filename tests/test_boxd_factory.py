"""Regression tests: production failures are owned by the machine, not operator."""
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

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
            self.assertEqual(r["processed"],1)
            self.assertEqual(r["release_status"],"HOLD")
            self.assertEqual(r["release_status"],"HOLD")

    def test_empty_input_cannot_pass(self):
        with tempfile.TemporaryDirectory() as td:
            d=pathlib.Path(td)
            t=d/"source.txt"
            t.write_text("quote")
            r=run([],t,d/"out")
            self.assertEqual(r["release_status"],"HOLD")
            self.assertEqual(r["passed"],0)


    def test_failed_gate_rules_feed_next_machine_render(self):
        with tempfile.TemporaryDirectory() as td:
            d=pathlib.Path(td)
            t=d/"source.txt"
            t.write_text("real quote",encoding="utf-8")
            observed=[]
            def fake_invoke(command,args,log):
                params=dict(zip(args[::2],args[1::2]))
                if command=="renderer":
                    repair=json.loads(pathlib.Path(params["--repair"]).read_text())
                    observed.append(repair["machine_action"])
                    pathlib.Path(params["--image"]).write_bytes(b"candidate")
                    pathlib.Path(params["--manifest"]).write_text(
                        json.dumps({"card_id":"BBP-001","quote":"real quote"}))
                else:
                    pathlib.Path(params["--report"]).write_text(
                        json.dumps({"inspector":"separate-process","border_intact":True,"text_legible":True}))
                return True
            failed={"verdict":"FAIL","checks":{"ONE_PORTRAIT_CARD":"FAIL"},
                    "remediation":{"policy_id":"BOXD_CI_FIRST_CARD_RULES_V2",
                                   "machine_action":"AUTO_REPAIR_AND_RERENDER_WITH_BOUNDED_RETRY",
                                   "failed_rules":[{"rule_id":"R001","check":"ONE_PORTRAIT_CARD","status":"FAIL"}]}}
            passed={"verdict":"PASS","checks":{"ONE_PORTRAIT_CARD":"PASS"},
                    "remediation":{"policy_id":"BOXD_CI_FIRST_CARD_RULES_V2",
                                   "machine_action":"ELIGIBLE_FOR_PROMOTION","failed_rules":[]}}
            with patch("boxd_factory.invoke",side_effect=fake_invoke), patch(
                    "boxd_factory.audit",side_effect=[failed,passed]):
                report=run([{"card_id":"BBP-001","quote":"real quote"}],t,d/"out",
                           renderer="renderer",inspector="inspector",max_attempts=3)
            self.assertEqual(observed,["INITIAL_RENDER","AUTO_REPAIR_AND_RERENDER_WITH_BOUNDED_RETRY"])
            self.assertEqual(report["cards"][0]["status"],"PASS")
            self.assertEqual(len(report["cards"][0]["attempts"]),2)
            self.assertEqual(report["release_status"],"HOLD") # Not 50.
            self.assertFalse((d/"out"/"candidate_release.zip").exists())


    def test_card_two_never_starts_when_card_one_fails(self):
        with tempfile.TemporaryDirectory() as td:
            d=pathlib.Path(td)
            transcript=d/"source.txt"
            transcript.write_text("quote",encoding="utf-8")
            report=run([{"card_id":"BBP-001","quote":"quote"},
                        {"card_id":"BBP-002","quote":"quote"}],
                       transcript,d/"out",max_attempts=2)
            self.assertEqual(report["processed"],1)
            self.assertEqual(report["cards"][0]["status"],"HOLD")
            self.assertFalse((d/"out"/"attempts"/"BBP-002").exists())
            self.assertEqual(report["release_status"],"HOLD")


    def test_pass_checkpoint_survives_restart_without_rendering_again(self):
        import hashlib
        with tempfile.TemporaryDirectory() as td:
            d=pathlib.Path(td)
            t=d/"source.txt"
            t.write_text("quote",encoding="utf-8")
            spec={"card_id":"BBP-001","quote":"quote"}
            calls=[]
            def fake_invoke(command,args,log):
                calls.append(command)
                p=dict(zip(args[::2],args[1::2]))
                if command=="renderer":
                    pathlib.Path(p["--image"]).write_bytes(b"image")
                    pathlib.Path(p["--manifest"]).write_text(json.dumps({
                        "card_id":"BBP-001","quote":"quote"}))
                else:
                    pathlib.Path(p["--report"]).write_text(json.dumps({
                        "inspector":"independent-inspector","border_intact":True,"text_legible":True}))
                return True
            verdict={"verdict":"PASS","checks":{"PNG_FORMAT":"PASS"},
                     "remediation":{"machine_action":"ELIGIBLE_FOR_PROMOTION","failed_rules":[]}}
            with patch("boxd_factory.invoke",side_effect=fake_invoke),patch("boxd_factory.audit",return_value=verdict):
                first=run([spec],t,d/"out",renderer="renderer",inspector="inspector")
                again=run([spec],t,d/"out",renderer="renderer",inspector="inspector")
            self.assertEqual(first["passed"],1)
            self.assertEqual(again["passed"],1)
            self.assertEqual(again["cards"][0]["checkpoint"],"RESTORED")
            self.assertEqual(calls,["renderer","inspector"])
            self.assertTrue((d/"out"/"accepted"/"BBP-001"/"checkpoint.json").exists())

    def test_tampered_checkpoint_blocks_repair_or_advance(self):
        with tempfile.TemporaryDirectory() as td:
            d=pathlib.Path(td)
            t=d/"source.txt"
            t.write_text("quote",encoding="utf-8")
            root=d/"out"/"accepted"/"BBP-001"
            root.mkdir(parents=True)
            (root/"checkpoint.json").write_text('{"state":"PASS_LOCKED"}')
            r=run([{"card_id":"BBP-001","quote":"quote"},
                   {"card_id":"BBP-002","quote":"quote"}],t,d/"out")
            self.assertEqual(r["processed"],1)
            self.assertEqual(r["cards"][0]["reason"],"INVALID_LOCKED_CHECKPOINT")
            self.assertFalse((d/"out"/"attempts"/"BBP-002").exists())

if __name__=="__main__":
    unittest.main()
