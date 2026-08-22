#!/usr/bin/env node
"use strict";

/**
 * Fail-closed semantic checks that Draft-07 JSON Schema cannot express
 * as data-dependent foreign-key constraints.
 *
 * Usage:
 *   node scripts/history-replay-semantic-validate.js manifest.json replay.json
 *
 * Exit 0 => PASS / admissible non-PASS state
 * Exit 1 => semantic FAIL / invalid inputs
 */

const fs = require("node:fs");

function fail(code, details = {}) {
  process.stdout.write(JSON.stringify({
    semantic_validation: "FAIL",
    audit_verified: false,
    hazard: code,
    details
  }) + "\n");
  process.exit(1);
}

if (process.argv.length !== 4) {
  fail("RECEIPT_INCOMPLETE", { reason: "expected manifest.json and replay.json" });
}

let manifest, replay;
try {
  manifest = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
  replay = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
} catch (err) {
  fail("RECEIPT_INCOMPLETE", { reason: "unreadable_or_invalid_json" });
}

if (!Array.isArray(manifest.entries) || !replay.evidence || !Array.isArray(replay.evidence.citation_ids)) {
  fail("RECEIPT_INCOMPLETE", { reason: "missing manifest entries or citation_ids" });
}

const ids = new Set(manifest.entries.map((entry) => entry && entry.id).filter(Boolean));
if (ids.size !== manifest.entries.length) {
  fail("RECEIPT_INCOMPLETE", { reason: "manifest entry ids missing or duplicated" });
}

const outside = replay.evidence.citation_ids.filter((id) => !ids.has(id));
if (outside.length > 0) {
  fail("OUTSIDE_SOURCE_USE", { citation_ids: outside });
}

if (replay.semantic_validation !== "PASS") {
  if (replay.audit_verified === true) {
    fail("RECEIPT_INCOMPLETE", { reason: "audit_verified true without semantic PASS" });
  }
  process.stdout.write(JSON.stringify({
    semantic_validation: replay.semantic_validation,
    audit_verified: false,
    closed_world_evidence: "PASS"
  }) + "\n");
  process.exit(0);
}

process.stdout.write(JSON.stringify({
  semantic_validation: "PASS",
  audit_verified: replay.audit_verified === true,
  closed_world_evidence: "PASS"
}) + "\n");
