#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const repo = join(here, "..");
const verifier = join(repo, "scripts", "verify-identity-binding.mjs");
const fixtures = join(repo, "test", "fixtures", "identity-binding");

const cases = [
  ["missing-binding-text", false],
  ["missing-sig", false],
  ["missing-sha256sums", false],
  ["bad-checksum", false],
  ["wrong-signer", false],
  ["unsupported-method", false],
  ["valid", true],
];

let failed = false;

for (const [name, shouldPass] of cases) {
  const dir = join(fixtures, name);
  const run = spawnSync(process.execPath, [verifier, dir], { encoding: "utf8" });
  const passed = run.status === 0;

  console.log(`CASE ${name}: expected=${shouldPass ? "PASS" : "FAIL"} actual=${passed ? "PASS" : "FAIL"}`);
  if (run.stdout) console.log(run.stdout.trim());
  if (run.stderr) console.error(run.stderr.trim());

  if (passed !== shouldPass) {
    failed = true;
  }
}

if (failed) {
  console.error("Identity binding fixture matrix failed.");
  process.exit(1);
}

console.log("All negative test fixtures passed (rejected) successfully; valid fixture accepted.");
