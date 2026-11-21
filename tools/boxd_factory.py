#!/usr/bin/env python3
"""BoxD production supervisor: machine-owned retries, receipts and release gate.

Renderer and independent inspector are external executables, NOT bundled here.
No adapter -> HOLD. No human QC step. No publication or merge in this runner.
"""
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import zipfile

from boxd_card_gate import audit

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def invoke(command, args, log):
    if not command:
        log.write_text("ADAPTER_NOT_CONFIGURED\n", encoding="utf-8")
        return False
    try:
        p = subprocess.run([command, *args], text=True, capture_output=True,
                           timeout=180, check=False)
        log.write_text(json.dumps({"exit_code":p.returncode,
            "stdout":p.stdout[-4000:], "stderr":p.stderr[-4000:]})+"\n", encoding="utf-8")
        return p.returncode == 0
    except (OSError, subprocess.TimeoutExpired) as e:
        log.write_text(type(e).__name__+": "+str(e)+"\n", encoding="utf-8")
        return False

def run(specs, transcript, out, renderer=None, inspector=None, max_attempts=3):
    out.mkdir(parents=True, exist_ok=True)
    receipts = []
    approved = []
    seen = set()
    for spec in specs:
        cid = spec.get("card_id", "")
        if not cid or cid in seen or "/" in cid or "\\" in cid or cid.startswith("."):
            receipts.append({"card_id":cid, "status":"HOLD", "reason":"INVALID_OR_DUPLICATE_ID"})
            continue
        seen.add(cid)
        result = {"card_id":cid, "status":"HOLD", "attempts":[]}
        for attempt in range(1, max_attempts+1):
            work = out/"attempts"/cid/str(attempt)
            work.mkdir(parents=True, exist_ok=True)
            spec_path = work/"spec.json"
            spec_path.write_text(json.dumps(spec,sort_keys=True,indent=2)+"\n",encoding="utf-8")
            image = work/"card.png"
            manifest = work/"manifest.json"
            visual = work/"inspection.json"
            rendering = invoke(renderer,
                ["--spec",str(spec_path),"--image",str(image),"--manifest",str(manifest),
                 "--transcript",str(transcript)],work/"renderer.log")
            if not rendering or not image.is_file() or not manifest.is_file():
                result["attempts"].append({"attempt":attempt,"verdict":"FAIL","reason":"RENDERER_FAILED"})
                continue
            inspected = invoke(inspector,
                ["--image",str(image),"--spec",str(spec_path),"--report",str(visual)],
                work/"inspector.log")
            if not inspected or not visual.is_file():
                result["attempts"].append({"attempt":attempt,"verdict":"HOLD","reason":"INSPECTOR_UNAVAILABLE"})
                continue
            try:
                inspection = json.loads(visual.read_text(encoding="utf-8"))
                m = json.loads(manifest.read_text(encoding="utf-8"))
                # Independent inspector must identify itself and return test evidence.
                if not inspection.get("inspector") or inspection["inspector"] == "generator":
                    raise ValueError("independent inspector identity missing")
                m["independent_visual_inspection"] = inspection
                m["image_sha256"] = digest(image)
                m["transcript_sha256"] = digest(transcript)
                m["attempt"] = attempt
                # Do not allow renderer/inspector to substitute another quote or card ID.
                if m.get("quote") != spec.get("quote") or m.get("card_id") != cid:
                    raise ValueError("rendered metadata diverged from locked spec")
                manifest.write_text(json.dumps(m,sort_keys=True,indent=2)+"\n",encoding="utf-8")
                verdict = audit(image,manifest,transcript)
                (work/"gate.json").write_text(json.dumps(verdict,indent=2)+"\n",encoding="utf-8")
                result["attempts"].append({"attempt":attempt,"verdict":verdict["verdict"],
                                           "checks":verdict["checks"],"sha256":digest(image)})
                if verdict["verdict"] == "PASS":
                    result["status"] = "PASS"
                    approved.append((cid,image,manifest,work/"gate.json"))
                    break
            except (ValueError,KeyError,TypeError, OSError, json.JSONDecodeError) as e:
                result["attempts"].append({"attempt":attempt,"verdict":"FAIL",
                                           "reason":"INVALID_INSPECTION_OR_MANIFEST",
                                           "detail":str(e)})
        receipts.append(result)
    passed = len(approved)
    complete = passed == len(specs) and len(specs) == 50 and len(seen) == 50
    report = {"policy":"BOXD_CI_FIRST_CARD_RULES_V2",
              "target":50,"passed":passed,"total":len(specs),
              "release_status":"READY_FOR_CREATIVE_APPROVAL" if complete else "HOLD",
              "human_qc_required":False,"cards":receipts}
    (out/"factory_report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    if complete:
        with zipfile.ZipFile(out/"candidate_release.zip","w",compression=zipfile.ZIP_DEFLATED) as z:
            for cid,img,manifest,gate in approved:
                z.write(img,f"cards/{cid}.png")
                z.write(manifest,f"receipts/{cid}.json")
                z.write(gate,f"audits/{cid}.json")
            z.write(out/"factory_report.json","factory_report.json")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--specs",type=pathlib.Path,required=True)
    p.add_argument("--transcript",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    p.add_argument("--renderer",help="Executable implementing --spec --image --manifest --transcript")
    p.add_argument("--inspector",help="Independent executable implementing --image --spec --report")
    a=p.parse_args()
    specs=json.loads(a.specs.read_text(encoding="utf-8"))
    if not isinstance(specs,list):
        p.error("specs must be a JSON list")
    report=run(specs,a.transcript,a.out,a.renderer,a.inspector)
    print(json.dumps({k:v for k,v in report.items() if k!="cards"},indent=2))
    return 0 if report["release_status"]=="READY_FOR_CREATIVE_APPROVAL" else 1

if __name__=="__main__":
    sys.exit(main())
