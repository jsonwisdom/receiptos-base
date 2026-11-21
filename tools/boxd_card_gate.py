#!/usr/bin/env python3
"""BoxD fail-closed collectible-card gate. Standard library only; never publishes."""
import argparse, hashlib, json, pathlib, struct, sys

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()

def dimensions(p):
    with open(p, "rb") as f:
        b = f.read(24)
    if len(b) != 24 or b[:8] != b"\x89PNG\r\n\x1a\n" or b[12:16] != b"IHDR":
        raise ValueError("not a PNG IHDR")
    return struct.unpack(">II", b[16:24])

def audit(image, manifest, transcript):
    m = json.loads(pathlib.Path(manifest).read_text(encoding="utf-8"))
    t = pathlib.Path(transcript).read_text(encoding="utf-8-sig")
    checks = {}
    try:
        w, h = dimensions(image)
        checks["PNG_FORMAT"] = "PASS"
        checks["ONE_PORTRAIT_CARD"] = "PASS" if h > w and abs(w/h - 5/7) <= 0.08 else "FAIL"
        checks["MIN_750x1050"] = "PASS" if w >= 750 and h >= 1050 else "FAIL"
    except ValueError:
        w = h = 0
        checks["PNG_FORMAT"] = checks["ONE_PORTRAIT_CARD"] = checks["MIN_750x1050"] = "FAIL"
    checks["IMAGE_SHA256"] = "PASS" if m.get("image_sha256") == sha256(image) else "FAIL"
    checks["SOURCE_SHA256"] = "PASS" if m.get("transcript_sha256") == sha256(transcript) else "FAIL"
    checks["EXACT_QUOTE"] = "PASS" if m.get("quote") and m["quote"] in t else "FAIL"
    checks["CARD_ID"] = "PASS" if isinstance(m.get("card_id"), str) and m["card_id"].strip() else "FAIL"
    checks["UNIQUE_CONCEPT"] = "PASS" if m.get("uniqueness_attested") is True and m.get("concept_set_hash") else "HOLD"
    vi = m.get("independent_visual_inspection") or {}
    independent = vi.get("inspector") not in (None, "", "generator")
    checks["COMPLETE_GRUBBY_BORDER"] = "PASS" if independent and vi.get("border_intact") is True else "HOLD"
    checks["LEGIBLE_TEXT"] = "PASS" if independent and vi.get("text_legible") is True else "HOLD"
    checks["AUDIO_CLAIM"] = "PASS" if m.get("audio_status") == "UNVERIFIED" or (m.get("audio_status") == "VERIFIED_WITH_RECEIPT" and m.get("audio_receipt_sha256")) else "FAIL"
    verdict = "FAIL" if "FAIL" in checks.values() else "HOLD" if "HOLD" in checks.values() else "PASS"
    return {"card_id": m.get("card_id"), "dimensions": [w, h], "checks": checks, "verdict": verdict, "policy": "BOXD_CI_FIRST_NO_FAKE_GREEN_V1"}

def main():
    p = argparse.ArgumentParser()
    for a in ("image", "manifest", "transcript"):
        p.add_argument("--" + a, required=True)
    p.add_argument("--report")
    a = p.parse_args()
    r = audit(a.image, a.manifest, a.transcript)
    payload = json.dumps(r, indent=2, sort_keys=True) + "\n"
    print(payload, end="")
    if a.report:
        pathlib.Path(a.report).write_text(payload, encoding="utf-8")
    return 0 if r["verdict"] == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())
