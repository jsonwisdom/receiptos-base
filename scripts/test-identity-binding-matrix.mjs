#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const repo = join(here, "..");
const verifier = join(repo, "scripts", "verify-identity-binding.mjs");

const bindingRel = "provenance/identity-binding/jaywisdom-identity-binding.txt";
const sigRel = "provenance/identity-binding/jaywisdom-identity-binding.sig";

const bindingText = `subject: jaywisdom.base.eth
ens: jaywisdom.eth
wallet: 0xA380552a27b0a5a2874Ea7AA52CAC09f542002E8
service: ReceiptOS Meme Court Frame MVP
endpoint: https://receiptos-frame-mvp.vercel.app
issue: jsonwisdom/receiptos-base#57
deployment_receipt: gcp-cloud-build:e0e45d99-ab21-49be-b675-bee556623283
court_state: FRAME_MVP_DEPLOYMENT_RECEIPT_VERIFIED
signature_gate: SIGNATURE_BUNDLE_PENDING
authority: false
truth_claim: false
`;

function sha256(text) {
  return createHash("sha256").update(text).digest("hex");
}

function sig(overrides = {}) {
  return JSON.stringify({
    schema: "RECEIPTOS_IDENTITY_BINDING_SIG_V1",
    signer: "0xA380552a27b0a5a2874Ea7AA52CAC09f542002E8",
    method: "personal_sign",
    signed_file: bindingRel,
    signature: `0x${"11".repeat(65)}`,
    msg: bindingText,
    message_hash: `0x${sha256(bindingText)}`,
    created_at: "2026-07-03T07:50:00Z",
    authority: false,
    truth_claim: false,
    test_signature: true,
    ...overrides,
  }, null, 2) + "\n";
}

function writeCase(root, name, options) {
  const dir = join(root, name);
  const prov = join(dir, "provenance", "identity-binding");
  mkdirSync(prov, { recursive: true });

  const binding = options.bindingText ?? bindingText;
  const signature = options.signatureText ?? sig(options.sigOverrides);

  if (!options.omitBinding) writeFileSync(join(dir, bindingRel), binding);
  if (!options.omitSig) writeFileSync(join(dir, sigRel), signature);

  if (!options.omitSums) {
    const bindingHash = options.badChecksum ? "0".repeat(64) : sha256(binding);
    const sigHash = options.badChecksum ? "1".repeat(64) : sha256(signature);
    writeFileSync(join(dir, "SHA256SUMS"), `${bindingHash}  ${bindingRel}\n${sigHash}  ${sigRel}\n`);
  }

  return dir;
}

const root = mkdtempSync(join(tmpdir(), "receiptos-identity-matrix-"));

const cases = [
  ["missing-binding-text", false, { omitBinding: true }],
  ["missing-sig", false, { omitSig: true }],
  ["missing-sha256sums", false, { omitSums: true }],
  ["bad-checksum", false, { badChecksum: true }],
  ["wrong-signer", false, { sigOverrides: { signer: "0x0000000000000000000000000000000000000000" } }],
  ["unsupported-method", false, { sigOverrides: { method: "unsupported" } }],
  ["signed-bytes-mismatch", false, { sigOverrides: { signed_file: "wrong-file.txt" } }],
  ["message-bytes-mismatch", false, { sigOverrides: { msg: `${bindingText}tampered\n` } }],
  ["valid", true, {}],
];

let failed = false;

try {
  for (const [name, shouldPass, options] of cases) {
    const dir = writeCase(root, name, options);
    const run = spawnSync(process.execPath, [verifier, dir], {
      encoding: "utf8",
      env: { ...process.env, RECEIPTOS_ALLOW_TEST_SIGNATURE: "1" },
    });
    const passed = run.status === 0;

    console.log(`CASE ${name}: expected=${shouldPass ? "PASS" : "FAIL"} actual=${passed ? "PASS" : "FAIL"}`);
    if (run.stdout) console.log(run.stdout.trim());
    if (run.stderr) console.error(run.stderr.trim());

    if (passed !== shouldPass) failed = true;
  }
} finally {
  rmSync(root, { recursive: true, force: true });
}

if (failed) {
  console.error("Identity binding fixture matrix failed.");
  process.exit(1);
}

console.log("All negative test fixtures passed (rejected) successfully; valid fixture accepted.");
