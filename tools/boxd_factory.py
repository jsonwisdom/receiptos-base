#!/usr/bin/env python3
"""BoxD production supervisor: machine-owned retries, receipts and release gate.

Renderer and independent inspector are external executables, NOT bundled here.
No adapter -> HOLD. No human QC step. No publication or merge in this runner.
"""
import argparse
import hashlib
import json
import pathlib
import os
import shutil
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

def atomic_json(path, payload):
    """Atomic checkpoint replacement: crash cannot expose a partially written JSON receipt."""
    temp = path.with_suffix(".pending")
    with temp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)

def checkpoint_files(out, cid):
    root = out/"accepted"/cid
    return root, root/"card.png", root/"manifest.json", root/"gate.json", root/"checkpoint.json"

def restore_checkpoint(out, cid, spec, transcript):
    root, image, manifest, gate, cp = checkpoint_files(out, cid)
    if not cp.is_file():
        return None
    # Fail closed on missing/corrupt artifacts, changed specs, changed source, or revoked checks.
    try:
        receipt = json.loads(cp.read_text(encoding="utf-8"))
        expected = {"card_id":cid, "spec_sha256":hashlib.sha256(
            json.dumps(spec,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
            "transcript_sha256":digest(transcript)}
        if any(receipt.get(k) != v for k,v in expected.items()):
            return None
        if any(not p.is_file() or digest(p) != receipt.get(key) for key,p in
               [("image_sha256",image),("manifest_sha256",manifest),("gate_sha256",gate)]):
            return None
        previous = json.loads(gate.read_text(encoding="utf-8"))
        if previous.get("verdict") != "PASS":
            return None
        checked = audit(image,manifest,transcript)
        if checked.get("verdict") != "PASS":
            return None
        return image,manifest,gate
    except (ValueError,TypeError,KeyError,OSError,json.JSONDecodeError):
        return None

def save_checkpoint(out, cid, spec, transcript, image, manifest, gate):
    root, target_image, target_manifest, target_gate, cp = checkpoint_files(out,cid)
    root.mkdir(parents=True,exist_ok=True)
    for source,target in [(image,target_image),(manifest,target_manifest),(gate,target_gate)]:
        staged = target.with_suffix(target.suffix+".pending")
        shutil.copyfile(source,staged)
        os.replace(staged,target)
    receipt = {
        "card_id":cid,
        "spec_sha256":hashlib.sha256(
            json.dumps(spec,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
        "transcript_sha256":digest(transcript),
        "image_sha256":digest(target_image),
        "manifest_sha256":digest(target_manifest),
        "gate_sha256":digest(target_gate),
        "state":"PASS_LOCKED"
    }
    atomic_json(cp,receipt)
    return target_image,target_manifest,target_gate

def run(specs, transcript, out, renderer=None, inspector=None, max_attempts=3):
    out.mkdir(parents=True, exist_ok=True)
    receipts = []
    approved = []
    seen = set()
    for spec in specs:
        cid = spec.get("card_id", "")
        if not cid or cid in seen or "/" in cid or "\\" in cid or cid.startswith("."):
            receipts.append({"card_id":cid, "status":"HOLD", "reason":"INVALID_OR_DUPLICATE_ID"})
            break
        seen.add(cid)
        cached = restore_checkpoint(out,cid,spec,transcript)
        if cached is not None:
            approved.append((cid,*cached))
            receipts.append({"card_id":cid,"status":"PASS","checkpoint":"RESTORED","attempts":[]})
            continue
        # Never overwrite or bypass an existing invalid lock; stop for machine investigation.
        if checkpoint_files(out,cid)[-1].exists():
            receipts.append({"card_id":cid,"status":"HOLD","reason":"INVALID_LOCKED_CHECKPOINT"})
            break
        result = {"card_id":cid, "status":"HOLD", "attempts":[]}
        repair = {"machine_action":"INITIAL_RENDER", "failed_rules":[], "policy_id":"BOXD_CI_FIRST_CARD_RULES_V2"}
        for attempt in range(1, max_attempts+1):
            work = out/"attempts"/cid/str(attempt)
            work.mkdir(parents=True, exist_ok=True)
            spec_path = work/"spec.json"
            spec_path.write_text(json.dumps(spec,sort_keys=True,indent=2)+"\n",encoding="utf-8")
            image = work/"card.png"
            manifest = work/"manifest.json"
            visual = work/"inspection.json"
            repair_path = work/"repair_input.json"
            repair_path.write_text(json.dumps(repair,sort_keys=True,indent=2)+"\n",encoding="utf-8")
            rendering = invoke(renderer,
                ["--spec",str(spec_path),"--image",str(image),"--manifest",str(manifest),
                 "--transcript",str(transcript),"--repair",str(repair_path)],work/"renderer.log")
            if not rendering or not image.is_file() or not manifest.is_file():
                result["attempts"].append({"attempt":attempt,"verdict":"FAIL","reason":"RENDERER_FAILED"})
                repair = {"machine_action":"REPAIR_RENDERER_FAILED","failed_rules":[{"check":"RENDERER_EXECUTION","status":"FAIL","action":"repair renderer output or invocation"}],"policy_id":"BOXD_CI_FIRST_CARD_RULES_V2"}
                continue
            inspected = invoke(inspector,
                ["--image",str(image),"--spec",str(spec_path),"--report",str(visual)],
                work/"inspector.log")
            if not inspected or not visual.is_file():
                result["attempts"].append({"attempt":attempt,"verdict":"HOLD","reason":"INSPECTOR_UNAVAILABLE"})
                repair = {"machine_action":"RESTORE_INDEPENDENT_INSPECTOR","failed_rules":[{"check":"INSPECTION_EXECUTION","status":"HOLD","action":"repair inspector invocation; do not approve without inspection"}],"policy_id":"BOXD_CI_FIRST_CARD_RULES_V2"}
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
                repair = verdict["remediation"]
                if verdict["verdict"] == "PASS":
                    result["status"] = "PASS"
                    locked=save_checkpoint(out,cid,spec,transcript,image,manifest,work/"gate.json")
                    approved.append((cid,*locked))
                    break
            except (ValueError,KeyError,TypeError, OSError, json.JSONDecodeError) as e:
                result["attempts"].append({"attempt":attempt,"verdict":"FAIL",
                                           "reason":"INVALID_INSPECTION_OR_MANIFEST",
                                           "detail":str(e)})
                repair = {"machine_action":"REPAIR_INSPECTION_OR_MANIFEST","failed_rules":[{"check":"INVALID_INSPECTION_OR_MANIFEST","status":"FAIL","action":str(e)}],"policy_id":"BOXD_CI_FIRST_CARD_RULES_V2"}
        result["final_remediation"] = repair if result["status"] != "PASS" else None
        receipts.append(result)
        # Strict serial production: no card N+1 until card N is independently PASS.
        if result["status"] != "PASS":
            break
    passed = len(approved)
    complete = passed == len(specs) and len(specs) == 50 and len(seen) == 50
    report = {"policy":"BOXD_CI_FIRST_CARD_RULES_V2",
              "target":50,"passed":passed,"total":len(specs),
              "processed":len(receipts),
              "next_card":specs[len(receipts)].get("card_id") if len(receipts)<len(specs) and receipts and receipts[-1]["status"]=="PASS" else None,
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
    p.add_argument("--renderer",help="Executable implementing --spec --image --manifest --transcript --repair")
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
