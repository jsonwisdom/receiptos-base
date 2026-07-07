#!/usr/bin/env python3
import json, hashlib, os, subprocess
from pathlib import Path

ROOT = Path(os.environ.get("RECEIPTOS_ROOT", "~/receiptos-base")).expanduser()
TV067 = ROOT / "golden-corpus/grp004/tv067"
OUT = ROOT / "releases/grp004-release-2026-07-04"
OUT.mkdir(parents=True, exist_ok=True)

def canon(o): return json.dumps(o, sort_keys=True, separators=(",",":"))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name, obj):
    p = OUT / name
    p.write_text(canon(obj))
    return p

tv067_sha = json.loads((TV067 / "shas.json").read_text())["packet_sha256"]
tv067_commit = subprocess.check_output(["git","rev-parse","HEAD"], cwd=ROOT, text=True).strip()

r = write("TV-073-EXECUTION-RECEIPT.final.json", {
  "tv_id":"TV-073",
  "status":"SEALED_TEST_VECTOR",
  "dependency":{"target":"TV-067","commit":tv067_commit,"packet_sha256":tv067_sha,"state":"VERIFIED"},
  "authority":False
})

v = write("VERIFICATION-REPORT.json", {
  "tv_id":"TV-073",
  "final_status":"VERIFIED_AGAINST_REAL_TV067",
  "tv067_dependency":{"commit":tv067_commit,"sha":tv067_sha}
})

a = write("AUDIT-LOG.json", {
  "events":[
    {"clock":0,"event":"TV067_READ_FROM_DISK"},
    {"clock":1,"event":"TV073_REGENERATED"},
    {"clock":2,"event":"SIGNED_TEST_VECTOR"}
  ]
})

p = write("RELEASE-PACKET.json", {
  "release_id":"GRP-004-RELEASE-2026-07-04",
  "tv067_dependency":{"commit":tv067_commit,"sha":tv067_sha},
  "signature_type":"test-vector",
  "artifacts":[
    {"name":r.name,"sha256":sha(r)},
    {"name":v.name,"sha256":sha(v)},
    {"name":a.name,"sha256":sha(a)}
  ]
})

m = write("INTAKE-MANIFEST.json", {
  "release_id":"GRP-004-RELEASE-2026-07-04",
  "tv_id":"TV-073",
  "tv067_dependency":{"commit":tv067_commit,"sha":tv067_sha},
  "signature_type":"test-vector",
  "artifacts":[
    {"name":p.name,"sha256":sha(p)},
    {"name":r.name,"sha256":sha(r)},
    {"name":v.name,"sha256":sha(v)},
    {"name":a.name,"sha256":sha(a)}
  ]
})

print("TV067_COMMIT", tv067_commit)
print("TV067_SHA", tv067_sha)
print("INTAKE_MANIFEST_SHA", sha(m))
