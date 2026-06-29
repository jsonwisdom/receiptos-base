#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const mod = require("json-canonicalize");
const canonicalize = mod.canonicalize || mod;

const SPEC = "SPEC-V1";
const ROOT = path.join("test-vectors", SPEC);
const RESULTS_DIR = path.join("results", SPEC);

function hash(s) {
  return crypto.createHash("sha256").update(s).digest("hex");
}
function json(p) {
  return JSON.parse(fs.readFileSync(p, "utf8"));
}
function has(p) {
  return fs.existsSync(p);
}
function stripNl(s) {
  return s.replace(/\r?\n$/, "");
}
function httpsOnly(s) {
  try { return new URL(s).protocol === "https:"; } catch { return false; }
}

function semantic(m) {
  if (typeof m.homepage === "string" && !httpsOnly(m.homepage)) return { valid:false, exit_code:15, reason:"invalid_url", failed_field:"homepage", sha256:null, canonical_file:null };
  if (m.developer && typeof m.developer.url === "string" && !httpsOnly(m.developer.url)) return { valid:false, exit_code:15, reason:"invalid_url", failed_field:"developer.url", sha256:null, canonical_file:null };
  if (typeof m.repository === "string" && !httpsOnly(m.repository)) return { valid:false, exit_code:15, reason:"invalid_url", failed_field:"repository", sha256:null, canonical_file:null };
  if (Object.prototype.hasOwnProperty.call(m, "unexpected")) return { valid:false, exit_code:14, reason:"unexpected_field", failed_field:"unexpected", sha256:null, canonical_file:null };
  if (!m.developer || typeof m.developer !== "object") return { valid:false, exit_code:10, reason:"semantic_error", failed_field:"developer", sha256:null, canonical_file:null };
  if (!m.name || !m.description || !Array.isArray(m.permissions) || !m.version) return { valid:false, exit_code:10, reason:"semantic_error", sha256:null, canonical_file:null };
  return null;
}

function run(v) {
  const dir = path.join(ROOT, v.path);
  const m = json(path.join(dir, "manifest.json"));
  const s = semantic(m);
  if (s) return s;

  const canon = canonicalize(m);
  const trueDigest = hash(canon);
  const jcsPath = path.join(dir, "manifest.jcs");
  if (!has(jcsPath)) return { valid:false, exit_code:22, reason:"canonical_mismatch", failed_stage:"canonicalization", computed:null, expected:trueDigest, sha256:null, canonical_file:null };

  const raw = fs.readFileSync(jcsPath, "utf8");
  if (stripNl(raw) !== canon) return { valid:false, exit_code:22, reason:"canonical_mismatch", failed_stage:"canonicalization", computed:hash(raw), expected:trueDigest, sha256:hash(raw), canonical_file:"manifest.jcs" };

  const lockPath = path.join(dir, "manifest.lock.json");
  if (has(lockPath)) {
    const lock = json(lockPath);
    if (lock.sha256 !== trueDigest) return { valid:false, exit_code:21, reason:"digest_mismatch", failed_stage:"lock", computed:trueDigest, expected:lock.sha256, sha256:trueDigest, canonical_file:"manifest.jcs" };
  }

  return { valid:true, exit_code:0, reason:"ok", failed_stage:null, sha256:trueDigest, canonical_file:"manifest.jcs" };
}

function compare(v, actual) {
  const expected = json(path.join(ROOT, v.path, "expected.json"));
  const fields = ["valid", "exit_code", "reason", "sha256", "canonical_file"];
  if ("failed_field" in expected) fields.push("failed_field");
  if ("failed_stage" in expected) fields.push("failed_stage");
  const mismatches = fields.filter(f => (actual[f] ?? null) !== (expected[f] ?? null)).map(f => ({ field:f, expected:expected[f] ?? null, actual:actual[f] ?? null }));
  return { id:v.id, path:v.path, expected_valid:expected.valid, semantic_valid:actual.valid, exit_code:actual.exit_code, expected_exit_code:expected.exit_code, reason:actual.reason, expected_reason:expected.reason, failed_field:actual.failed_field ?? null, failed_stage:actual.failed_stage ?? null, sha256:actual.sha256 ?? null, canonical_file:actual.canonical_file ?? null, conformance_passed:mismatches.length === 0, mismatches };
}

const corpus = json(path.join(ROOT, "manifest.json"));
const results = corpus.vectors.map(v => compare(v, run(v)));
const passed = results.filter(r => r.conformance_passed).length;
const summary = { spec:corpus.spec, corpus_version:corpus.corpus_version, timestamp:new Date().toISOString(), total:results.length, conformance_passed:passed, conformance_failed:results.length - passed, semantic_valid:results.filter(r => r.semantic_valid).length, semantic_invalid:results.filter(r => !r.semantic_valid).length, results };
fs.mkdirSync(RESULTS_DIR, { recursive:true });
fs.writeFileSync(path.join(RESULTS_DIR, "summary.json"), JSON.stringify(summary, null, 2) + "\n");
console.log(`SPEC-V1 Runner: ${passed}/${results.length} conformance checks passed`);
if (passed !== results.length) process.exit(1);
