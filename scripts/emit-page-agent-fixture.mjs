import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const { sha256 } = require("../adapters/page-agent/hash");
const {
  createPageAgentWireEvent,
  canonicalJson,
  verifyWireEventSchema
} = require("../adapters/page-agent/wire-event");

const repoRoot = path.resolve(__dirname, "..");
const fixturePath = path.join(repoRoot, "adapters/page-agent/tests/fixture.dom.html");
const artifactDir = path.join(repoRoot, "artifacts/page-agent");
const jsonPath = path.join(artifactDir, "wireevent.fixture.json");
const shaPath = path.join(artifactDir, "wireevent.fixture.sha256");

const command = "Click the Verify Receipt button";
const timestamp = 1783036800000;

function deterministicExecutor({ command, dom }) {
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

const domBefore = fs.readFileSync(fixturePath, "utf8");
const { domAfter, action_result } = deterministicExecutor({ command, dom: domBefore });

const wireEvent = createPageAgentWireEvent({
  payload: action_result,
  domBefore,
  domAfter,
  command,
  timestamp
});

const schemaResult = verifyWireEventSchema(wireEvent);
if (!schemaResult.ok) {
  throw new Error(`WireEvent schema validation failed: ${schemaResult.reason}`);
}

const canonicalPayload = canonicalJson(wireEvent);
const digest = sha256(canonicalPayload);

fs.mkdirSync(artifactDir, { recursive: true });
fs.writeFileSync(jsonPath, `${canonicalPayload}\n`, "utf8");
fs.writeFileSync(shaPath, `${digest}  wireevent.fixture.json\n`, "utf8");

process.stdout.write(`${canonicalPayload}\n`);
process.stderr.write(`sha256 ${digest}\n`);
