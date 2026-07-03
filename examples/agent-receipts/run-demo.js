#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const { canonicalize, sha256Ref } = require("./canonical");
const { computePolicyHash } = require("./evaluate-policy");

const ROOT = path.resolve(__dirname, "../..");
const POLICY_PATH = path.join(ROOT, "policy", "agent-receipts", "default-policy.json");
const FIXTURE_DIR = path.join(__dirname, "fixtures");

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function contentPreimage(receipt) {
  return {
    inputs: receipt.inputs,
    outputs: receipt.outputs,
    captured_context: receipt.captured_context,
    policy_hash: receipt.policy.policy_hash,
    manifest_hash: receipt.manifest_hash,
    parent_hash: receipt.parent_hash,
  };
}

function withoutSignature(receipt) {
  const clone = JSON.parse(JSON.stringify(receipt));
  delete clone.signature;
  return clone;
}

function computeContentHash(receipt) {
  return sha256Ref(contentPreimage(receipt));
}

function verifySignature(receipt) {
  if (!receipt.signature || receipt.signature.scheme !== "ed25519") {
    return false;
  }

  const publicKey = crypto.createPublicKey({
    key: Buffer.from(receipt.signature.public_key, "hex"),
    format: "der",
    type: "spki",
  });

  return crypto.verify(
    null,
    Buffer.from(canonicalize(withoutSignature(receipt))),
    publicKey,
    Buffer.from(receipt.signature.value, "base64"),
  );
}

function verifyPolicyHash(receipt, policy) {
  const currentPolicyHash = computePolicyHash(policy);
  if (!receipt.policy || receipt.policy.policy_hash !== currentPolicyHash) {
    return {
      terminal: "STALE",
      reason: "policy_hash mismatch",
      recorded_policy_hash: receipt.policy && receipt.policy.policy_hash,
      current_policy_hash: currentPolicyHash,
    };
  }
  return null;
}

function verifyReceipt(receipt, policy = readJson(POLICY_PATH)) {
  if (typeof receipt !== "object" || receipt === null) {
    return { terminal: "REJECTED", reason: "malformed receipt" };
  }

  if (receipt.authority !== false) {
    return { terminal: "REJECTED", reason: "authority must be false" };
  }

  if (!verifySignature(receipt)) {
    return { terminal: "REJECTED", reason: "invalid signature" };
  }

  const stale = verifyPolicyHash(receipt, policy);
  if (stale) {
    return stale;
  }

  const replayed = computeContentHash(receipt);
  if (replayed !== receipt.content_hash || receipt.receipt_id !== receipt.content_hash) {
    return {
      terminal: "MISMATCHED",
      reason: "content_hash replay mismatch",
      replayed_content_hash: replayed,
      recorded_content_hash: receipt.content_hash,
    };
  }

  return { terminal: "VERIFIED", replayed_content_hash: replayed };
}

function loadFixture(name) {
  return readJson(path.join(FIXTURE_DIR, name));
}

function assertTerminal(label, result, expected) {
  if (result.terminal !== expected) {
    throw new Error(`${label}: expected ${expected}, got ${result.terminal}: ${result.reason || ""}`);
  }
}

function assertPolicy(label, receipt, expected) {
  if (!receipt.policy_result || receipt.policy_result.pass !== expected) {
    throw new Error(`${label}: expected policy pass=${expected}`);
  }
}

function printTrace(label, receipt, result) {
  console.log([
    `${label}: terminal=${result.terminal}`,
    `policy_pass=${receipt.policy_result && receipt.policy_result.pass}`,
    `content_hash=${receipt.content_hash}`,
    `policy_hash=${receipt.policy && receipt.policy.policy_hash}`,
    `reason=${result.reason || "ok"}`,
  ].join(" "));
}

function main() {
  const policy = readJson(POLICY_PATH);

  const cases = [
    {
      file: "valid.receipt.json",
      label: "valid receipt",
      expectedTerminal: "VERIFIED",
      expectedPolicyPass: true,
    },
    {
      file: "policy-denied.receipt.json",
      label: "policy denied receipt",
      expectedTerminal: "VERIFIED",
      expectedPolicyPass: false,
    },
    {
      file: "stale.receipt.json",
      label: "stale receipt",
      expectedTerminal: "STALE",
      expectedPolicyPass: true,
    },
    {
      file: "rejected.receipt.json",
      label: "rejected receipt",
      expectedTerminal: "REJECTED",
      expectedPolicyPass: true,
    },
    {
      file: "mismatched.receipt.json",
      label: "mismatched receipt",
      expectedTerminal: "MISMATCHED",
      expectedPolicyPass: true,
    },
  ];

  for (const testCase of cases) {
    const receipt = loadFixture(testCase.file);
    const result = verifyReceipt(receipt, policy);
    assertPolicy(testCase.label, receipt, testCase.expectedPolicyPass);
    assertTerminal(testCase.label, result, testCase.expectedTerminal);
    printTrace(testCase.label, receipt, result);
  }

  console.log("fixture_trace: pass");
  console.log("authority: false");
}

if (require.main === module) {
  main();
}

module.exports = {
  computeContentHash,
  contentPreimage,
  verifyPolicyHash,
  verifyReceipt,
  verifySignature,
};
