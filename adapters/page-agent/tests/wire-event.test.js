const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const { runVerifiedPageAction } = require("../index");
const { toWireEvent, verifyWireEventSchema, WIRE_EVENT_TYPE } = require("../wire-event");

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

test("WireEvent maps PageAgent receipt without side effects", async () => {
  const domBefore = loadFixture();
  const receipt = await runVerifiedPageAction({
    command,
    domBefore,
    execute: deterministicExecutor,
    timestamp: "2026-07-03T00:00:00.000Z"
  });

  const event = toWireEvent({ receipt, command, domBefore, sequence: 1 });

  assert.equal(event.type, WIRE_EVENT_TYPE);
  assert.equal(event.payload.receipt_type, receipt.type);
  assert.equal(event.payload.command_hash, receipt.command_hash);
  assert.equal(event.payload.dom_before_hash, receipt.dom_before_hash);
  assert.equal(event.payload.dom_after_hash, receipt.dom_after_hash);
  assert.equal(event.authority, false);
  assert.equal(event.payload.authority, false);
  assert.equal(event.witness_only, true);
  assert.equal(event.side_effect, false);
  assert.deepEqual(verifyWireEventSchema(event), { ok: true });
});

test("WireEvent schema fails closed on authority drift", async () => {
  const domBefore = loadFixture();
  const receipt = await runVerifiedPageAction({
    command,
    domBefore,
    execute: deterministicExecutor,
    timestamp: "2026-07-03T00:00:00.000Z"
  });

  const event = toWireEvent({ receipt, command, domBefore, sequence: 1 });
  event.authority = true;

  assert.deepEqual(verifyWireEventSchema(event), { ok: false, reason: "authority drift" });
});

test("WireEvent mapping rejects mismatched DOM before hash", async () => {
  const domBefore = loadFixture();
  const receipt = await runVerifiedPageAction({
    command,
    domBefore,
    execute: deterministicExecutor,
    timestamp: "2026-07-03T00:00:00.000Z"
  });

  assert.throws(() => {
    toWireEvent({ receipt, command, domBefore: domBefore + "\n<!-- drift -->", sequence: 1 });
  }, /DOM before hash mismatch/);
});
