const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const { sha256 } = require("../hash");
const { runVerifiedPageAction } = require("../index");
const { verifyReceiptSchema, verifyReplayParity } = require("../verifier");

const fixturePath = path.join(__dirname, "fixture.dom.html");
const command = "Click the Verify Receipt button";

function loadFixture() {
  return fs.readFileSync(fixturePath, "utf8");
}

async function deterministicExecutor({ command, dom }) {
  if (command !== "Click the Verify Receipt button") {
    throw new Error("unsupported command in fixture executor");
  }

  return {
    domAfter: dom.replace('<div id="status">idle</div>', '<div id="status">verified</div>'),
    action_result: {
      action_type: "click",
      selected_element: "#verify-btn",
      status_transition: "idle -> verified"
    }
  };
}

test("Invariant #1: same command plus same DOM yields same command and before hashes", async () => {
  const domBefore = loadFixture();
  const timestamp = "2026-07-03T00:00:00.000Z";

  const first = await runVerifiedPageAction({ command, domBefore, execute: deterministicExecutor, timestamp });
  const second = await runVerifiedPageAction({ command, domBefore, execute: deterministicExecutor, timestamp });

  assert.equal(first.command_hash, second.command_hash);
  assert.equal(first.dom_before_hash, second.dom_before_hash);
  assert.equal(first.command_hash, sha256(command));
  assert.equal(first.dom_before_hash, sha256(domBefore));
});

test("Invariant #2: mutation captures before and after hashes with authority false", async () => {
  const domBefore = loadFixture();
  const receipt = await runVerifiedPageAction({
    command,
    domBefore,
    execute: deterministicExecutor,
    timestamp: "2026-07-03T00:00:00.000Z"
  });

  const domAfter = domBefore.replace('<div id="status">idle</div>', '<div id="status">verified</div>');

  assert.notEqual(receipt.dom_before_hash, receipt.dom_after_hash);
  assert.equal(receipt.dom_before_hash, sha256(domBefore));
  assert.equal(receipt.dom_after_hash, sha256(domAfter));
  assert.equal(receipt.authority, false);
});

test("Invariant #3: receipt schema compliance", async () => {
  const receipt = await runVerifiedPageAction({
    command,
    domBefore: loadFixture(),
    execute: deterministicExecutor,
    timestamp: "2026-07-03T00:00:00.000Z"
  });

  assert.deepEqual(verifyReceiptSchema(receipt), { ok: true });
});

test("Invariant #4: replay parity reproduces dom_after_hash", async () => {
  const domBefore = loadFixture();
  const receipt = await runVerifiedPageAction({
    command,
    domBefore,
    execute: deterministicExecutor,
    timestamp: "2026-07-03T00:00:00.000Z"
  });

  const replayResult = await verifyReplayParity({
    command,
    domBefore,
    receipt,
    replay: deterministicExecutor
  });

  assert.deepEqual(replayResult, { ok: true });
});
