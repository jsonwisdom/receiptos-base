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

function buildCase(manifest, options = {}) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "farcaster-fuzz-vector-"));
  const canonical = options.canonical !== undefined ? options.canonical : canonicalize(manifest);
  const manifestPath = path.join(dir, "manifest.json");
  const canonicalPath = path.join(dir, "manifest.jcs");
  const lockPath = path.join(dir, "manifest.lock.json");
  const lock = {
    manifest_id: options.manifestId || manifest.id,
    manifest_path: canonicalPath,
    canonical_source: options.canonicalSource || "manifest.jcs",
    canonicalization: options.canonicalization || "RFC8785",
    sha256: options.sha256 || sha256(canonical),
    created_at: options.createdAt || "2026-06-29T01:00:00Z",
    status: "LOCKED",
    authority: options.authority === undefined ? false : options.authority
  };

  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
  fs.writeFileSync(canonicalPath, canonical);
  fs.writeFileSync(lockPath, JSON.stringify(lock, null, 2));
  return { manifestPath, canonicalPath, lockPath };
}

function runSemantic(paths) {
  return spawnSync("node", [semanticVerifier], {
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

function expectPass(name, manifest, options) {
  const result = runSemantic(buildCase(manifest, options));
  if (result.status !== 0) {
    console.error(`::error::Valid fuzz control failed: ${name}`);
    console.error(result.stdout || "");
    console.error(result.stderr || "");
    process.exit(1);
  }
  console.log(`PASS fuzz control accepted: ${name}`);
}

function expectFail(name, manifest, options) {
  const result = runSemantic(buildCase(manifest, options));
  if (result.status === 0) {
    console.error(`::error::Fuzz mutation unexpectedly passed: ${name}`);
    process.exit(1);
  }
  console.log(`PASS fuzz mutation rejected: ${name}`);
}

expectPass("base manifest", clone(baseManifest));

const mutations = [
  ["uppercase id", (m) => { m.id = "JayWisdom"; }],
  ["space in id", (m) => { m.id = "jay wisdom"; }],
  ["id too short", (m) => { m.id = "jw"; }],
  ["empty name", (m) => { m.name = ""; }],
  ["empty description", (m) => { m.description = ""; }],
  ["missing developer object", (m) => { delete m.developer; }],
  ["empty developer name", (m) => { m.developer.name = ""; }],
  ["non-https developer", (m) => { m.developer.url = "http://github.com/jsonwisdom/receiptos-base"; }],
  ["ftp website", (m) => { m.website = "ftp://cmptrwsdm.com"; }],
  ["missing app", (m) => { delete m.app; }],
  ["non-https app", (m) => { m.app.url = "http://cmptrwsdm.com/app"; }],
  ["permissions not array", (m) => { m.app.permissions = "farcaster.read"; }],
  ["empty permissions string", (m) => { m.app.permissions = [""]; }],
  ["unknown permission", (m) => { m.app.permissions = ["farcaster.delete"]; }],
  ["non-https icon", (m) => { m.icon = "http://cmptrwsdm.com/icon.png"; }],
  ["non-png icon", (m) => { m.icon = "https://cmptrwsdm.com/icon.jpg"; }],
  ["screenshots missing", (m) => { delete m.screenshots; }],
  ["screenshots empty", (m) => { m.screenshots = []; }],
  ["screenshot not https", (m) => { m.screenshots = ["http://cmptrwsdm.com/screenshot-1.png"]; }],
  ["screenshot not image", (m) => { m.screenshots = ["https://cmptrwsdm.com/screenshot-1.txt"]; }]
];

for (const [name, mutate] of mutations) {
  const manifest = clone(baseManifest);
  mutate(manifest);
  expectFail(name, manifest);
}

expectFail("canonical drift single byte", clone(baseManifest), {
  canonical: canonicalize(baseManifest).replace("JAYWISDOM", "JAYWISDOM!")
});

expectFail("lock authority elevation", clone(baseManifest), { authority: true });
expectFail("lock canonicalization downgrade", clone(baseManifest), { canonicalization: "STABLE_JSON" });
expectFail("lock source drift", clone(baseManifest), { canonicalSource: "manifest.json" });
expectFail("lock id drift", clone(baseManifest), { manifestId: "jsonwisdom" });
expectFail("lock hash drift", clone(baseManifest), { sha256: "f".repeat(64) });
expectFail("lock future date", clone(baseManifest), { createdAt: new Date(Date.now() + 86400000).toISOString() });

console.log("Deterministic Farcaster manifest fuzz vectors passed.");
