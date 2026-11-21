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
    def test_eight_cards_are_eight_individual_artifacts_not_one_sheet(self):
        with tempfile.TemporaryDirectory() as td:
            d=pathlib.Path(td)
            source=d/"source.txt"
            source.write_text("quote", encoding="utf-8")
            one_sheet=[{"card_id":"BBP-001","quote":"quote","artifact_type":"contact_sheet"}]
            r=run(one_sheet, source, d/"out")
            self.assertEqual(r["release_status"],"HOLD")
            self.assertEqual(r["reason"],"EXACTLY_EIGHT_INDIVIDUAL_CARD_SPECS_REQUIRED")
            self.assertFalse((d/"out"/"candidate_release.zip").exists())

    def test_extra_covers_and_ten_card_order_fail_before_render(self):
        with tempfile.TemporaryDirectory() as td:
            d=pathlib.Path(td)
            source=d/"source.txt"
            source.write_text("quote", encoding="utf-8")
            for count in (7, 9, 10):
                specs=[{"card_id":f"BBP-{i:03d}","quote":"quote"} for i in range(1,count+1)]
                r=run(specs,source,d/f"out-{count}")
                self.assertEqual(r["release_status"],"HOLD")
                self.assertEqual(r["processed"],0)
            specs=[{"card_id":f"BBP-{i:03d}","quote":"quote"} for i in range(1,9)]
            specs[7]["artifact_type"]="cover"
            r=run(specs,source,d/"out-cover")
            self.assertEqual(r["release_status"],"HOLD")
            self.assertFalse((d/"out-cover"/"attempts").exists())

    def test_missing_adapters_fail_closed_and_preserve_receipts(self):
        with tempfile.TemporaryDirectory() as td:
            d=pathlib.Path(td)
            transcript=d/"transcript.txt"
            transcript.write_text("Exact source quote",encoding="utf-8")
            report=run([{"card_id":"BBP-001","quote":"Exact source quote"}],
                       transcript,d/"out",max_attempts=3)
            self.assertEqual(report["release_status"],"HOLD")
            self.assertFalse(report["human_qc_required"])
            self.assertEqual(len(report["cards"][0]["attempts"]),1)
            self.assertFalse((d/"out"/"candidate_release.zip").exists())
            self.assertTrue((d/"out"/"factory_report.json").exists())
            self.assertTrue((d/"out"/"attempts"/"BBP-001"/"1"/"renderer.log").exists())

    def test_duplicate_ids_are_rejected_without_overwriting(self):
        with tempfile.TemporaryDirectory() as td:
            d=pathlib.Path(td)
            t=d/"source.txt"
            t.write_text("quote",encoding="utf-8")
            r=run([{"card_id":"BBP-001","quote":"quote"},
                   {"card_id":"BBP-001","quote":"quote"}],t,d/"out",max_attempts=1)
            self.assertEqual(r["processed"],1)
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


    def test_unchanged_failure_stops_retry_spending(self):
        with tempfile.TemporaryDirectory() as td:
            d=pathlib.Path(td)
            transcript=d/"source.txt"
            transcript.write_text("quote", encoding="utf-8")
            rendered=[]
            def fake_invoke(command,args,log):
                p=dict(zip(args[::2],args[1::2]))
                if command=="renderer":
                    rendered.append(p["--image"])
                    pathlib.Path(p["--image"]).write_bytes(b"same-defective-artwork")
                    pathlib.Path(p["--manifest"]).write_text(json.dumps(
                        {"card_id":"BBP-001","quote":"quote"}))
                else:
                    pathlib.Path(p["--report"]).write_text(json.dumps(
                        {"inspector":"separate-process","border_intact":False,
                         "text_legible":True}))
                return True
            fail={"verdict":"FAIL","checks":{"COMPLETE_GRUBBY_BORDER":"FAIL"},
                "remediation":{"machine_action":"AUTO_REPAIR_AND_RERENDER_WITH_BOUNDED_RETRY",
                               "failed_rules":[{"rule_id":"R005"}]}}
            with patch("boxd_factory.invoke",side_effect=fake_invoke),patch(
                "boxd_factory.audit",return_value=fail):
                report=run([{"card_id":"BBP-001","quote":"quote"}],
                           transcript,d/"out",renderer="renderer",
                           inspector="inspector",max_attempts=100)
            self.assertEqual(len(rendered),2)
            self.assertEqual(report["cards"][0]["attempts"][-1]["reason"],
                             "IDENTICAL_FAILED_ARTWORK")
            self.assertEqual(report["release_status"],"HOLD")
            self.assertFalse((d/"out"/"candidate_release.zip").exists())


    def test_card_number_controls_sequence_and_routine(self):
        with tempfile.TemporaryDirectory() as td:
            d=pathlib.Path(td)
            t=d/"source.txt"
            t.write_text("quote", encoding="utf-8")
            result=run([{"card_id":"BBP-20261120-002","quote":"quote"}],
                       t,d/"out",max_attempts=1)
            self.assertEqual(result["cards"][0]["reason"],
                             "INVALID_DUPLICATE_OR_OUT_OF_ORDER_CARD_NUMBER")
            self.assertEqual(result["cards"][0]["expected_card_number"],1)
            self.assertFalse((d/"out"/"attempts").exists())

    def test_numbered_routine_is_written_to_renderer_input(self):
        with tempfile.TemporaryDirectory() as td:
            d=pathlib.Path(td)
            t=d/"source.txt"
            t.write_text("quote",encoding="utf-8")
            run([{"card_id":"BBP-20261120-001","quote":"quote"}],
                t,d/"out",max_attempts=1)
            repair=json.loads((d/"out"/"attempts"/"BBP-20261120-001"/"1"/"repair_input.json").read_text())
            self.assertEqual(repair["card_number"],1)
            self.assertEqual(repair["card_id"],"BBP-20261120-001")
            self.assertEqual(repair["routine"],"RENDER")

if __name__=="__main__":
    unittest.main()
