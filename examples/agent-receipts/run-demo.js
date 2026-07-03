#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const { canonicalize, sha256Ref } = require("./canonical");
const { computePolicyHash, evaluatePolicy } = require("./evaluate-policy");

const ROOT = path.resolve(__dirname, "../..");
const RECEIPT_PATH = path.join(ROOT, "receipts", "agent-demo.receipt.json");
const POLICY_DENIED_RECEIPT_PATH = path.join(ROOT, "receipts", "agent-demo-policy-denied.receipt.json");
const INPUT_PATH = path.join(__dirname, "tool-call.input.json");
const OUTPUT_PATH = path.join(__dirname, "tool-call.output.json");
const POLICY_PATH = path.join(ROOT, "policy", "agent-receipts", "default-policy.json");

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

function signReceipt(receipt, privateKey, publicKeyHex) {
  const body = withoutSignature(receipt);
  const signature = crypto.sign(null, Buffer.from(canonicalize(body)), privateKey).toString("base64");
  return {
    ...receipt,
    signature: {
      scheme: "ed25519",
      public_key: publicKeyHex,
      value: signature,
    },
  };
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

function verifyReceipt(receipt) {
  if (typeof receipt !== "object" || receipt === null) {
    return { terminal: "REJECTED", reason: "malformed receipt" };
  }
  if (receipt.authority !== false) {
    return { terminal: "REJECTED", reason: "authority must be false" };
  }
  if (!verifySignature(receipt)) {
    return { terminal: "REJECTED", reason: "invalid signature" };
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

function buildReceiptDraft({ input, output, actionType, capturedContext, parentHash }) {
  const policy = readJson(POLICY_PATH);
  const policyHash = computePolicyHash(policy);

  const manifest = {
    files: [
      path.relative(ROOT, INPUT_PATH),
      path.relative(ROOT, OUTPUT_PATH),
      path.relative(ROOT, POLICY_PATH),
    ],
  };

  const draft = {
    receipt_version: "agent-receipt/v0.2",
    receipt_id: null,
    timestamp: "2026-07-02T00:00:00Z",
    agent_id: "example-agent",
    action_type: actionType,
    inputs: input,
    outputs: output,
    captured_context: capturedContext,
    policy: {
      version: policy.policy_version,
      policy_hash: policyHash,
      policy_id: policy.policy_id,
    },
    policy_result: null,
    parent_hash: parentHash,
    manifest_hash: sha256Ref(manifest),
    content_hash: null,
    authority: false,
  };

  draft.policy_result = evaluatePolicy(policy, draft);
  draft.content_hash = computeContentHash(draft);
  draft.receipt_id = draft.content_hash;
  return draft;
}

function makeSignedReceipt(options, signingKeypair) {
  const draft = buildReceiptDraft(options);
  return signReceipt(
    draft,
    signingKeypair.privateKey,
    signingKeypair.publicKey.export({ format: "der", type: "spki" }).toString("hex"),
  );
}

function assertTerminal(name, actual, expected) {
  if (actual.terminal !== expected) {
    throw new Error(`${name}: expected ${expected}, got ${actual.terminal}: ${actual.reason || ""}`);
  }
  console.log(`${name}: ${actual.terminal}`);
}

function assertPolicy(name, receipt, expected) {
  if (!receipt.policy_result || receipt.policy_result.pass !== expected) {
    throw new Error(`${name}: expected policy pass=${expected}`);
  }
  console.log(`${name}: policy pass=${expected}`);
}

function main() {
  fs.mkdirSync(path.dirname(RECEIPT_PATH), { recursive: true });

  const signingKeypair = crypto.generateKeyPairSync("ed25519");
  const input = readJson(INPUT_PATH);
  const output = readJson(OUTPUT_PATH);

  const receipt = makeSignedReceipt({
    input,
    output,
    actionType: "tool_call",
    capturedContext: [
      {
        type: "recorded_transformation",
        value: "echo returned the same message supplied in inputs",
      },
    ],
    parentHash: null,
  }, signingKeypair);

  fs.writeFileSync(RECEIPT_PATH, `${JSON.stringify(receipt, null, 2)}\n`);

  assertPolicy("valid receipt", receipt, true);
  assertTerminal("valid receipt", verifyReceipt(receipt), "VERIFIED");

  const policyDeniedReceipt = makeSignedReceipt({
    input: {
      tool_name: "llm",
      prompt: "generate nondeterministic text",
    },
    output: {
      text: "uncaptured sample",
    },
    actionType: "llm_call",
    capturedContext: [],
    parentHash: receipt.content_hash,
  }, signingKeypair);

  fs.writeFileSync(POLICY_DENIED_RECEIPT_PATH, `${JSON.stringify(policyDeniedReceipt, null, 2)}\n`);

  assertPolicy("policy denied receipt", policyDeniedReceipt, false);
  assertTerminal("policy denied receipt", verifyReceipt(policyDeniedReceipt), "VERIFIED");

  const tampered = JSON.parse(JSON.stringify(receipt));
  tampered.outputs.output.message = "tampered output";
  assertTerminal("tampered receipt", verifyReceipt(tampered), "REJECTED");

  const unsignedMismatch = JSON.parse(JSON.stringify(receipt));
  unsignedMismatch.content_hash = sha256Ref("validly signed by a future fixture but replay divergent");
  unsignedMismatch.signature = undefined;
  const mismatchKeypair = crypto.generateKeyPairSync("ed25519");
  const resigned = signReceipt(
    unsignedMismatch,
    mismatchKeypair.privateKey,
    mismatchKeypair.publicKey.export({ format: "der", type: "spki" }).toString("hex"),
  );
  assertTerminal("valid signature with replay divergence", verifyReceipt(resigned), "MISMATCHED");

  console.log(`receipt_written: ${path.relative(ROOT, RECEIPT_PATH)}`);
  console.log(`policy_denied_receipt_written: ${path.relative(ROOT, POLICY_DENIED_RECEIPT_PATH)}`);
  console.log("authority: false");
}

if (require.main === module) {
  main();
}

module.exports = {
  buildReceiptDraft,
  computeContentHash,
  contentPreimage,
  makeSignedReceipt,
  verifyReceipt,
  verifySignature,
};
