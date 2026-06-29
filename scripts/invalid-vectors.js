#!/usr/bin/env node
"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const crypto = require("crypto");
const { spawnSync } = require("child_process");
const { canonicalize } = require("json-canonicalize");

const root = process.cwd();
const semanticVerifier = path.join(root, "scripts", "semantic-verify.js");
const lockVerifier = path.join(root, "scripts", "verify-manifest-lock.js");

const baseManifest = {
  id: "jaywisdom",
  name: "JAYWISDOM",
  description: "Replay-first verification on Base. Replay First. Verify Everything.",
  developer: {
    name: "jsonwisdom",
    url: "https://github.com/jsonwisdom/receiptos-base"
  },
  website: "https://cmptrwsdm.com",
  icon: "https://cmptrwsdm.com/icon.png",
  screenshots: ["https://cmptrwsdm.com/screenshot-1.png"],
  app: {
    url: "https://cmptrwsdm.com/app",
    permissions: ["farcaster.read", "farcaster.write"]
  }
};

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function sha256(text) {
  return crypto.createHash("sha256").update(text).digest("hex");
}

function writeCase(vector) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "farcaster-invalid-vector-"));
  const manifest = vector.manifest || clone(baseManifest);
  const canonical = vector.canonical !== undefined ? vector.canonical : canonicalize(manifest);
  const lock = vector.lock || {
    manifest_id: manifest.id,
    manifest_path: path.join(dir, "manifest.jcs"),
    canonical_source: "manifest.jcs",
    canonicalization: "RFC8785",
    sha256: sha256(canonical),
    created_at: "2026-06-29T01:00:00Z",
    status: "LOCKED",
    authority: false
  };

  const manifestPath = path.join(dir, "manifest.json");
  const canonicalPath = path.join(dir, "manifest.jcs");
  const lockPath = path.join(dir, "manifest.lock.json");

  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
  fs.writeFileSync(canonicalPath, canonical);
  fs.writeFileSync(lockPath, JSON.stringify(lock, null, 2));

  return { dir, manifestPath, canonicalPath, lockPath };
}

function runNode(script, paths) {
  return spawnSync("node", [script], {
    cwd: root,
    env: {
      ...process.env,
      MANIFEST_PATH: paths.manifestPath,
      MANIFEST_JCS_PATH: paths.canonicalPath,
      MANIFEST_LOCK_PATH: paths.lockPath
    },
    encoding: "utf8"
  });
}

function mustFail(vector) {
  const paths = writeCase(vector);
  const result = runNode(vector.verifier === "lock" ? lockVerifier : semanticVerifier, paths);
  if (result.status === 0) {
    console.error(`::error::Invalid vector unexpectedly passed: ${vector.name}`);
    process.exit(1);
  }
  const output = `${result.stdout || ""}\n${result.stderr || ""}`;
  if (vector.expect && !output.includes(vector.expect)) {
    console.error(`::error::Invalid vector failed with unexpected error: ${vector.name}`);
    console.error(`Expected substring: ${vector.expect}`);
    console.error(output);
    process.exit(1);
  }
  console.log(`PASS invalid vector rejected: ${vector.name}`);
}

const futureDate = new Date(Date.now() + 86400000).toISOString();

const vectors = [
  {
    name: "empty developer.url rejected",
    expect: "developer.url must not be an empty string",
    manifest: (() => { const m = clone(baseManifest); m.developer.url = ""; return m; })()
  },
  {
    name: "http app.url rejected",
    expect: "app.url must be HTTPS",
    manifest: (() => { const m = clone(baseManifest); m.app.url = "http://cmptrwsdm.com/app"; return m; })()
  },
  {
    name: "http icon rejected",
    expect: "icon must be an HTTPS URL",
    manifest: (() => { const m = clone(baseManifest); m.icon = "http://cmptrwsdm.com/icon.png"; return m; })()
  },
  {
    name: "missing screenshot rejected",
    expect: "at least one screenshot is required",
    manifest: (() => { const m = clone(baseManifest); m.screenshots = []; return m; })()
  },
  {
    name: "bad permission rejected",
    expect: "invalid permission",
    manifest: (() => { const m = clone(baseManifest); m.app.permissions = ["farcaster.admin"]; return m; })()
  },
  {
    name: "http website rejected",
    expect: "website must be HTTPS",
    manifest: (() => { const m = clone(baseManifest); m.website = "http://cmptrwsdm.com"; return m; })()
  },
  {
    name: "canonical byte drift rejected",
    expect: "manifest.json does not match manifest.jcs RFC8785 canonical bytes",
    canonical: canonicalize(baseManifest).replace("JAYWISDOM", "JAYWISDOMX")
  },
  {
    name: "lock authority true rejected",
    expect: "lock authority must remain false",
    lock: (() => { const c = canonicalize(baseManifest); return { manifest_id: "jaywisdom", manifest_path: "MANIFEST_PATH_REPLACED", canonical_source: "manifest.jcs", canonicalization: "RFC8785", sha256: sha256(c), created_at: "2026-06-29T01:00:00Z", status: "LOCKED", authority: true }; })()
  },
  {
    name: "lock canonicalization drift rejected",
    expect: "lock canonicalization must be RFC8785",
    lock: (() => { const c = canonicalize(baseManifest); return { manifest_id: "jaywisdom", manifest_path: "MANIFEST_PATH_REPLACED", canonical_source: "manifest.jcs", canonicalization: "STABLE_JSON", sha256: sha256(c), created_at: "2026-06-29T01:00:00Z", status: "LOCKED", authority: false }; })()
  },
  {
    name: "lock manifest_id drift rejected",
    expect: "manifest_id drift",
    lock: (() => { const c = canonicalize(baseManifest); return { manifest_id: "wrong-id", manifest_path: "MANIFEST_PATH_REPLACED", canonical_source: "manifest.jcs", canonicalization: "RFC8785", sha256: sha256(c), created_at: "2026-06-29T01:00:00Z", status: "LOCKED", authority: false }; })()
  },
  {
    name: "future dated lock rejected",
    expect: "lock created_at must not be future-dated",
    lock: (() => { const c = canonicalize(baseManifest); return { manifest_id: "jaywisdom", manifest_path: "MANIFEST_PATH_REPLACED", canonical_source: "manifest.jcs", canonicalization: "RFC8785", sha256: sha256(c), created_at: futureDate, status: "LOCKED", authority: false }; })()
  },
  {
    name: "lock sha256 drift rejected",
    expect: "lock sha256 drift",
    lock: (() => { return { manifest_id: "jaywisdom", manifest_path: "MANIFEST_PATH_REPLACED", canonical_source: "manifest.jcs", canonicalization: "RFC8785", sha256: "0".repeat(64), created_at: "2026-06-29T01:00:00Z", status: "LOCKED", authority: false }; })()
  }
];

for (const vector of vectors) {
  const c = vector.canonical !== undefined ? vector.canonical : canonicalize(vector.manifest || baseManifest);
  if (vector.lock && vector.lock.manifest_path === "MANIFEST_PATH_REPLACED") {
    vector.lock.manifest_path = "__TEMP__";
  }
  const originalWriteCase = writeCase;
  if (vector.lock && vector.lock.manifest_path === "__TEMP__") {
    const originalLock = vector.lock;
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "farcaster-invalid-vector-"));
    originalLock.manifest_path = path.join(dir, "manifest.jcs");
    const manifest = vector.manifest || clone(baseManifest);
    const canonical = vector.canonical !== undefined ? vector.canonical : canonicalize(manifest);
    const manifestPath = path.join(dir, "manifest.json");
    const canonicalPath = path.join(dir, "manifest.jcs");
    const lockPath = path.join(dir, "manifest.lock.json");
    fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
    fs.writeFileSync(canonicalPath, canonical);
    fs.writeFileSync(lockPath, JSON.stringify(originalLock, null, 2));
    const result = runNode(vector.verifier === "lock" ? lockVerifier : semanticVerifier, { manifestPath, canonicalPath, lockPath });
    if (result.status === 0) {
      console.error(`::error::Invalid vector unexpectedly passed: ${vector.name}`);
      process.exit(1);
    }
    const output = `${result.stdout || ""}\n${result.stderr || ""}`;
    if (vector.expect && !output.includes(vector.expect)) {
      console.error(`::error::Invalid vector failed with unexpected error: ${vector.name}`);
      console.error(`Expected substring: ${vector.expect}`);
      console.error(output);
      process.exit(1);
    }
    console.log(`PASS invalid vector rejected: ${vector.name}`);
  } else {
    mustFail(vector);
  }
}

console.log("Invalid Farcaster manifest vectors passed.");
