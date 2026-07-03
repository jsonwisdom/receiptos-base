const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const { emitPageAgentWireEvent, runVerifiedPageAction } = require("../index");
const {
  DEFAULT_RECIPIENT,
  WIRE_EVENT_TYPE,
  createPageAgentWireEvent,
  toWireEvent,
  verifyWireEventSchema
} = require("../wire-event");

const fixturePath = path.join(__dirname, "fixture.dom.html");
const command = "Click the Verify Receipt button";
const timestampMs = 1783036800000;

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

function assertBytes32(value) {
  assert.match(value, /^0x[0-9a-f]{64}$/);
}

test("WireEvent maps PageAgent receipt to EAS schema fields", async () => {
  const domBefore = loadFixture();
  const receipt = await runVerifiedPageAction({
    command,
    domBefore,
    execute: deterministicExecutor,
    timestampMs
  });

  const event = toWireEvent({ receipt, command, domBefore });

  assert.equal(event.event_type, WIRE_EVENT_TYPE);
  assert.equal(event.version, "0.1.0");
  assert.equal(event.timestamp, timestampMs);
  assert.equal(event.recipient, DEFAULT_RECIPIENT);
  assert.equal(event.replay_required, true);
  assert.equal(event.authority, false);
  assert.equal(event.receipt_type, receipt.type);
  assertBytes32(event.payload_hash);
  assertBytes32(event.command_hash);
  assertBytes32(event.dom_before_hash);
  assertBytes32(event.dom_after_hash);
  assert.deepEqual(verifyWireEventSchema(event), { ok: true });
});

test("WireEvent schema fails closed on authority drift", async () => {
  const domBefore = loadFixture();
  const receipt = await runVerifiedPageAction({
    command,
    domBefore,
    execute: deterministicExecutor,
    timestampMs
  });

  const event = toWireEvent({ receipt, command, domBefore });
  event.authority = true;

  assert.deepEqual(verifyWireEventSchema(event), { ok: false, reason: "authority drift" });
});

test("WireEvent mapping rejects mismatched DOM before hash", async () => {
  const domBefore = loadFixture();
  const receipt = await runVerifiedPageAction({
    command,
    domBefore,
    execute: deterministicExecutor,
    timestampMs
  });

  assert.throws(() => {
    toWireEvent({ receipt, command, domBefore: domBefore + "\n<!-- drift -->" });
  }, /DOM before hash mismatch/);
});

test("createPageAgentWireEvent emits directly from payload and DOM", async () => {
  const domBefore = loadFixture();
  const { domAfter, action_result } = await deterministicExecutor({ command, dom: domBefore });
  const event = createPageAgentWireEvent({
    payload: action_result,
    domBefore,
    domAfter,
    command,
    timestamp: timestampMs
  });

  assert.equal(event.event_type, WIRE_EVENT_TYPE);
  assert.equal(event.recipient, DEFAULT_RECIPIENT);
  assert.equal(event.replay_required, true);
  assert.equal(event.authority, false);
  assert.deepEqual(verifyWireEventSchema(event), { ok: true });
});

test("emitPageAgentWireEvent returns receipt plus schema-aligned event", async () => {
  const domBefore = loadFixture();
  const output = await emitPageAgentWireEvent({
    command,
    domBefore,
    execute: deterministicExecutor,
    timestampMs
  });

  assert.equal(output.receipt.authority, false);
  assert.equal(output.wire_event.authority, false);
  assert.equal(output.wire_event.replay_required, true);
  assert.deepEqual(verifyWireEventSchema(output.wire_event), { ok: true });
});
