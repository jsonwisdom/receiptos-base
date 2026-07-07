const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const test = require("node:test");
const { runL1Verification } = require("../packages/receiptos-core/verifier.js");

test("same input produces identical receipt id and event hash", async () => {
  const first = await runL1Verification({ input: "0xTestInput123" });
  const second = await runL1Verification({ input: "0xTestInput123" });

  assert.equal(first.receipt_id, second.receipt_id);
  assert.equal(first.event_hash, second.event_hash);
  assert.equal(first.authority, false);
  assert.equal(first.truth_claim, false);
  assert.equal(first.observed, true);
  assert.equal(first.verified, false);
  assert.equal(first.metadata.observed_not_verified, true);
});

test("live mode is deterministic external pending", async () => {
  const first = await runL1Verification({ input: "jaywisdom.base.eth", live: true });
  const second = await runL1Verification({ input: "jaywisdom.base.eth", live: true });

  assert.equal(first.status, "EXTERNAL_PENDING");
  assert.equal(first.receipt_id, second.receipt_id);
  assert.equal(first.event_hash, second.event_hash);
  assert.equal(first.authority, false);
  assert.equal(first.truth_claim, false);
  assert.equal(first.verified, false);
});

test("core files do not use time or browser crypto for receipt identity", () => {
  const verifier = readFileSync("packages/receiptos-core/verifier.js", "utf8");
  const canonical = readFileSync("packages/receiptos-core/canonical.js", "utf8");
  const source = `${verifier}\n${canonical}`;

  assert.equal(source.includes("Date.now"), false);
  assert.equal(source.includes("new Date"), false);
  assert.equal(source.includes("crypto.subtle"), false);
  assert.equal(source.includes("json-canonicalize"), true);
});
