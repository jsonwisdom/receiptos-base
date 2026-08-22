"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const validator = path.join(__dirname, "..", "scripts", "history-replay-semantic-validate.js");

function run(manifest, replay) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "history-replay-"));
  const manifestPath = path.join(dir, "manifest.json");
  const replayPath = path.join(dir, "replay.json");
  fs.writeFileSync(manifestPath, JSON.stringify(manifest));
  fs.writeFileSync(replayPath, JSON.stringify(replay));
  const result = spawnSync(process.execPath, [validator, manifestPath, replayPath], { encoding: "utf8" });
  fs.rmSync(dir, { recursive: true, force: true });
  return { ...result, json: JSON.parse(result.stdout) };
}

const manifest = {
  version: "0.1",
  manifest_id: "fixture",
  entries: [{ id: "SOURCE_1" }],
};

test("closed-world citation passes when citation id is sealed", () => {
  const result = run(manifest, {
    evidence: { citation_ids: ["SOURCE_1"] },
    semantic_validation: "PASS",
    audit_verified: true,
  });

  assert.equal(result.status, 0);
  assert.equal(result.json.closed_world_evidence, "PASS");
  assert.equal(result.json.audit_verified, true);
});

test("outside source fails closed and clears audit verification", () => {
  const result = run(manifest, {
    evidence: { citation_ids: ["UNSEALED_SOURCE"] },
    semantic_validation: "PASS",
    audit_verified: true,
  });

  assert.equal(result.status, 1);
  assert.equal(result.json.semantic_validation, "FAIL");
  assert.equal(result.json.audit_verified, false);
  assert.equal(result.json.hazard, "OUTSIDE_SOURCE_USE");
});

test("audit_verified cannot survive a non-PASS semantic state", () => {
  const result = run(manifest, {
    evidence: { citation_ids: ["SOURCE_1"] },
    semantic_validation: "PENDING",
    audit_verified: true,
  });

  assert.equal(result.status, 1);
  assert.equal(result.json.audit_verified, false);
  assert.equal(result.json.hazard, "RECEIPT_INCOMPLETE");
});
