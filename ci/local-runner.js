#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const mod = require("json-canonicalize");
const canonicalize = mod.canonicalize || mod;

const VECTOR_ROOT = "test-vectors";
const ROOT_MANIFEST = path.join(VECTOR_ROOT, "manifest.json");

function argValue(name) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : null;
}
function hashBytes(buf) {
  return crypto.createHash("sha256").update(buf).digest("hex");
}
function hashText(s) {
  return hashBytes(Buffer.from(s, "utf8"));
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

function runVector(root, v) {
  const dir = path.join(root, v.path);
  const m = json(path.join(dir, "manifest.json"));
  const s = semantic(m);
  if (s) return s;

  const canon = canonicalize(m);
  const trueDigest = hashText(canon);
  const jcsPath = path.join(dir, "manifest.jcs");
  if (!has(jcsPath)) return { valid:false, exit_code:22, reason:"canonical_mismatch", failed_stage:"canonicalization", computed:null, expected:trueDigest, sha256:null, canonical_file:null };

  const raw = fs.readFileSync(jcsPath, "utf8");
  if (stripNl(raw) !== canon) return { valid:false, exit_code:22, reason:"canonical_mismatch", failed_stage:"canonicalization", computed:hashText(raw), expected:trueDigest, sha256:hashText(raw), canonical_file:"manifest.jcs" };

  const lockPath = path.join(dir, "manifest.lock.json");
  if (has(lockPath)) {
    const lock = json(lockPath);
    if (lock.sha256 !== trueDigest) return { valid:false, exit_code:21, reason:"digest_mismatch", failed_stage:"lock", computed:trueDigest, expected:lock.sha256, sha256:trueDigest, canonical_file:"manifest.jcs" };
  }

  return { valid:true, exit_code:0, reason:"ok", failed_stage:null, sha256:trueDigest, canonical_file:"manifest.jcs" };
}

function compare(root, v, actual) {
  const expected = json(path.join(root, v.path, "expected.json"));
  const fields = ["valid", "exit_code", "reason", "sha256", "canonical_file"];
  if ("failed_field" in expected) fields.push("failed_field");
  if ("failed_stage" in expected) fields.push("failed_stage");
  const mismatches = fields.filter(f => (actual[f] ?? null) !== (expected[f] ?? null)).map(f => ({ field:f, expected:expected[f] ?? null, actual:actual[f] ?? null }));
  return { id:v.id, path:v.path, expected_valid:expected.valid, semantic_valid:actual.valid, exit_code:actual.exit_code, expected_exit_code:expected.exit_code, reason:actual.reason, expected_reason:expected.reason, failed_field:actual.failed_field ?? null, failed_stage:actual.failed_stage ?? null, sha256:actual.sha256 ?? null, canonical_file:actual.canonical_file ?? null, conformance_passed:mismatches.length === 0, mismatches };
}

function verifySealedSpec(spec) {
  if (!spec.sealed) return null;
  if (!spec.manifest_sha256) return { field:"manifest_sha256", expected:"present", actual:null };
  const actual = hashBytes(fs.readFileSync(path.join(VECTOR_ROOT, spec.path)));
  return actual === spec.manifest_sha256 ? null : { field:"manifest_sha256", expected:spec.manifest_sha256, actual };
}

function runSpec(spec) {
  const manifestPath = path.join(VECTOR_ROOT, spec.path || path.join(spec.id, "manifest.json"));
  const root = path.dirname(manifestPath);
  const corpus = json(manifestPath);
  const sealedMismatch = verifySealedSpec(spec);
  const results = corpus.vectors.map(v => compare(root, v, runVector(root, v)));
  const passed = results.filter(r => r.conformance_passed).length;
  const summary = { spec:corpus.spec, corpus_version:corpus.corpus_version, sealed:!!spec.sealed, sealed_manifest_ok:!sealedMismatch, sealed_manifest_mismatch:sealedMismatch, timestamp:new Date().toISOString(), total:results.length, conformance_passed:passed, conformance_failed:results.length - passed, semantic_valid:results.filter(r => r.semantic_valid).length, semantic_invalid:results.filter(r => !r.semantic_valid).length, results };
  const outDir = path.join("results", corpus.spec);
  fs.mkdirSync(outDir, { recursive:true });
  fs.writeFileSync(path.join(outDir, "summary.json"), JSON.stringify(summary, null, 2) + "\n");
  console.log(corpus.spec + " Runner: " + passed + "/" + results.length + " conformance checks passed");
  return summary;
}

const requestedSpec = argValue("--spec");
let specs;
if (has(ROOT_MANIFEST)) {
  const root = json(ROOT_MANIFEST);
  specs = root.specs || [];
} else {
  specs = [{ id:"SPEC-V1", path:"SPEC-V1/manifest.json", sealed:false }];
}
if (requestedSpec) specs = specs.filter(s => s.id === requestedSpec);
if (specs.length === 0) {
  console.error("No matching specs found");
  process.exit(1);
}

const summaries = specs.map(runSpec);
const rootSummary = { timestamp:new Date().toISOString(), total_specs:summaries.length, specs:summaries.map(s => ({ spec:s.spec, conformance_passed:s.conformance_passed, conformance_failed:s.conformance_failed, sealed_manifest_ok:s.sealed_manifest_ok })) };
fs.mkdirSync("results", { recursive:true });
fs.writeFileSync(path.join("results", "summary.json"), JSON.stringify(rootSummary, null, 2) + "\n");

if (summaries.some(s => s.conformance_failed > 0 || !s.sealed_manifest_ok)) process.exit(1);
