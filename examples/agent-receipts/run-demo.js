#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "../..");
const RECEIPT_PATH = path.join(ROOT, "receipts", "agent-demo.receipt.json");
const INPUT_PATH = path.join(__dirname, "tool-call.input.json");
const OUTPUT_PATH = path.join(__dirname, "tool-call.output.json");
const POLICY_PATH = path.join(ROOT, "policy", "agent-receipts", "default-policy.json");

function stable(value) {
  if (value === null || typeof value !== "object") {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map(stable).join(",")}]`;
  }
  const keys = Object.keys(value).sort();
  return `{${keys.map((key) => `${JSON.stringify(key)}:${stable(value[key])}`).join(",")}}`;
}

function sha256Hex(value) {
  const bytes = typeof value === "string" ? value : stable(value);
  return crypto.createHash("sha256").update(bytes, "utf8").digest("hex");
}

function sha256Ref(value) {
  return `sha256:${sha256Hex(value)}`;
}

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
  const signature = crypto.sign(null, Buffer.from(stable(body)), privateKey).toString("base64");
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
    Buffer.from(stable(withoutSignature(receipt))),
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

function makeReceipt() {
  const input = readJson(INPUT_PATH);
  const output = readJson(OUTPUT_PATH);
  const policy = readJson(POLICY_PATH);
  const policyHash = sha256Ref(policy);

  const manifest = {
    files: [
      path.relative(ROOT, INPUT_PATH),
      path.relative(ROOT, OUTPUT_PATH),
      path.relative(ROOT, POLICY_PATH),
    ],
  };

  const receipt = {
    receipt_version: "agent-receipt/v0.2",
    receipt_id: null,
    timestamp: "2026-07-02T00:00:00Z",
    agent_id: "example-agent",
    action_type: "tool_call",
    inputs: input,
    outputs: output,
    captured_context: [
      {
        type: "recorded_transformation",
        value: "echo returned the same message supplied in inputs",
      },
    ],
    policy: {
      version: policy.policy_version || "0.1.0",
      policy_hash: policyHash,
      policy_id: policy.policy_id,
    },
    policy_result: {
      pass: true,
      details: {
        rules: (policy.rules || []).map((rule) => ({
          rule_id: rule.rule_id,
          result: "pass",
        })),
      },
    },
    parent_hash: null,
    manifest_hash: sha256Ref(manifest),
    content_hash: null,
    authority: false,
  };

  receipt.content_hash = computeContentHash(receipt);
  receipt.receipt_id = receipt.content_hash;

  const { publicKey, privateKey } = crypto.generateKeyPairSync("ed25519");
  const publicKeyHex = publicKey.export({ format: "der", type: "spki" }).toString("hex");
  return signReceipt(receipt, privateKey, publicKeyHex);
}

function assertTerminal(name, actual, expected) {
  if (actual.terminal !== expected) {
    throw new Error(`${name}: expected ${expected}, got ${actual.terminal}: ${actual.reason || ""}`);
  }
  console.log(`${name}: ${actual.terminal}`);
}

function main() {
  fs.mkdirSync(path.dirname(RECEIPT_PATH), { recursive: true });

  const receipt = makeReceipt();
  fs.writeFileSync(RECEIPT_PATH, `${JSON.stringify(receipt, null, 2)}\n`);

  const verified = verifyReceipt(receipt);
  assertTerminal("valid receipt", verified, "VERIFIED");

  const tampered = JSON.parse(JSON.stringify(receipt));
  tampered.outputs.output.message = "tampered output";
  assertTerminal("tampered receipt", verifyReceipt(tampered), "REJECTED");

  const unsignedMismatch = JSON.parse(JSON.stringify(receipt));
  unsignedMismatch.content_hash = sha256Ref("validly signed by a future fixture but replay divergent");
  const { publicKey, privateKey } = crypto.generateKeyPairSync("ed25519");
  unsignedMismatch.signature = undefined;
  const resigned = signReceipt(
    unsignedMismatch,
    privateKey,
    publicKey.export({ format: "der", type: "spki" }).toString("hex"),
  );
  assertTerminal("valid signature with replay divergence", verifyReceipt(resigned), "MISMATCHED");

  console.log(`receipt_written: ${path.relative(ROOT, RECEIPT_PATH)}`);
  console.log("authority: false");
}

main();
