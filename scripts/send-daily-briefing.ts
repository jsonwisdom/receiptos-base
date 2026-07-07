import { createHash } from "node:crypto";
import tls from "node:tls";
import { createWalletClient, encodeAbiParameters, http, parseAbi } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { base } from "viem/chains";

const SMTP_HOST = "smtp.gmail.com";
const SMTP_PORT = 465;
const CANONICALIZER_VERSION = "CANONICAL_SERIALIZATION_RULES_V1";
const GENESIS_PREV_WITNESS_HASH = `sha256:${"0".repeat(64)}`;

type WorkflowWitness = {
  repo: string;
  workflow: string;
  status: string;
  conclusion?: string | null;
  run_url?: string | null;
  timestamp?: string | null;
};

type CalendarWitness = {
  title?: string;
  event?: string;
  start: string;
  end?: string | null;
  url?: string | null;
};

type DeploymentWitness = {
  surface: string;
  status: string;
  url?: string | null;
  timestamp?: string | null;
};

type DailyBriefingWitness = {
  canonicalizer_version: string;
  calendar: CalendarWitness[];
  deployments: DeploymentWitness[];
  generated_at: string;
  github_workflows: WorkflowWitness[];
  invariants: {
    authority: false;
    fail_closed: true;
    no_summaries_no_scores: true;
    replayable: true;
    truth_claim: false;
    witness_only: true;
  };
  prev_witness_hash: string;
  replay_hash: string | null;
  repo_commit: string;
  witness_hash: string | null;
  workflow_run_id: string;
};

type EasPayload = {
  witness_hash: string;
  prev_witness_hash: string;
  replay_hash: string;
  repo_commit: string;
  workflow_run_id: string;
  canonicalizer_version: string;
  generated_at: string;
  authority: false;
  truth_claim: false;
};

function readJsonEnv<T>(name: string, fallback: T): T {
  const value = process.env[name];
  if (!value) return fallback;

  try {
    return JSON.parse(value) as T;
  } catch (error) {
    throw new Error(`Invalid JSON in ${name}: ${(error as Error).message}`);
  }
}

function sha256Hex(bytes: Buffer | string): string {
  return `sha256:${createHash("sha256").update(bytes).digest("hex")}`;
}

function normalizeCanonicalValue(value: unknown): unknown {
  if (value === null || value === undefined) return value;
  if (typeof value === "string") return value.normalize("NFC").trim();
  if (typeof value === "number") {
    if (!Number.isInteger(value)) throw new Error("CANONICALIZATION_FAILURE floats_not_allowed");
    return value;
  }
  if (typeof value === "boolean") return value;
  if (Array.isArray(value)) return value.map(normalizeCanonicalValue);
  if (typeof value === "object") {
    const input = value as Record<string, unknown>;
    const output: Record<string, unknown> = {};
    for (const key of Object.keys(input).sort()) {
      const fieldValue = input[key];
      if (fieldValue === undefined) continue;
      output[key.normalize("NFC").trim()] = normalizeCanonicalValue(fieldValue);
    }
    return output;
  }
  throw new Error(`CANONICALIZATION_FAILURE unsupported_type=${typeof value}`);
}

function canonicalJson(value: unknown): string {
  return JSON.stringify(normalizeCanonicalValue(value));
}

function sealWitness(witness: DailyBriefingWitness): DailyBriefingWitness {
  const replayBasis: DailyBriefingWitness = { ...witness, replay_hash: null, witness_hash: null };
  const replay_hash = sha256Hex(canonicalJson(replayBasis));
  const witnessBasis: DailyBriefingWitness = { ...witness, replay_hash, witness_hash: null };
  const witness_hash = sha256Hex(canonicalJson(witnessBasis));
  return { ...witness, replay_hash, witness_hash };
}

function renderWorkflowRows(items: WorkflowWitness[]): string {
  if (items.length === 0) return "_No GitHub workflow witnesses supplied._";

  return [
    "| Repo | Workflow | Status | Conclusion | Timestamp | Run |",
    "|---|---|---|---|---|---|",
    ...items.map((item) => {
      const run = item.run_url ? `[run](${item.run_url})` : "missing";
      return `| ${item.repo} | ${item.workflow} | ${item.status} | ${item.conclusion ?? "missing"} | ${item.timestamp ?? "missing"} | ${run} |`;
    }),
  ].join("\n");
}

function renderDeploymentRows(items: DeploymentWitness[]): string {
  if (items.length === 0) return "_No deployment witnesses supplied._";

  return [
    "| Surface | Status | Timestamp | URL |",
    "|---|---|---|---|",
    ...items.map((item) => {
      const url = item.url ? `[open](${item.url})` : "missing";
      return `| ${item.surface} | ${item.status} | ${item.timestamp ?? "missing"} | ${url} |`;
    }),
  ].join("\n");
}

function renderCalendarRows(items: CalendarWitness[]): string {
  if (items.length === 0) return "_No calendar witnesses supplied._";

  return [
    "| Title | Start | End | URL |",
    "|---|---|---|---|",
    ...items.map((item) => {
      const title = item.title ?? item.event ?? "missing";
      const url = item.url ? `[open](${item.url})` : "missing";
      return `| ${title} | ${item.start} | ${item.end ?? "missing"} | ${url} |`;
    }),
  ].join("\n");
}

export function renderDailyBriefing(witness: DailyBriefingWitness): string {
  return `# JayOps Daily Briefing

Generated: ${witness.generated_at}
Canonicalizer: ${witness.canonicalizer_version}
Repo commit: ${witness.repo_commit}
Workflow run: ${witness.workflow_run_id}
Previous witness hash: ${witness.prev_witness_hash}
Replay hash: ${witness.replay_hash ?? "missing"}
Witness hash: ${witness.witness_hash ?? "missing"}

## Invariants

\`\`\`json
${JSON.stringify(witness.invariants, null, 2)}
\`\`\`

## GitHub Workflow Witnesses

${renderWorkflowRows(witness.github_workflows)}

## Deployment Witnesses

${renderDeploymentRows(witness.deployments)}

## Calendar Witnesses

${renderCalendarRows(witness.calendar)}

---

No truth claims. No scores. No risk summaries. Witness objects only. authority=false.
`;
}

function encodeHeader(value: string): string {
  return value.replace(/[\r\n]/g, " ");
}

function buildMimeMessage({ to, from, subject, body }: { to: string; from: string; subject: string; body: string }): string {
  const lines = [
    `From: ${encodeHeader(from)}`,
    `To: ${encodeHeader(to)}`,
    `Subject: ${encodeHeader(subject)}`,
    "MIME-Version: 1.0",
    'Content-Type: text/plain; charset="UTF-8"',
    "Content-Transfer-Encoding: 8bit",
    "",
    body,
  ];

  return lines.join("\r\n");
}

function waitFor(socket: tls.TLSSocket, expectedCodes: string[]): Promise<string> {
  return new Promise((resolve, reject) => {
    let buffer = "";
    const timeout = setTimeout(() => {
      cleanup();
      reject(new Error(`SMTP_TIMEOUT expected=${expectedCodes.join(",")}`));
    }, 15000);

    const cleanup = () => {
      clearTimeout(timeout);
      socket.off("data", onData);
      socket.off("error", onError);
    };

    const onError = (error: Error) => {
      cleanup();
      reject(error);
    };

    const onData = (chunk: Buffer) => {
      buffer += chunk.toString("utf8");
      const lines = buffer.split(/\r?\n/).filter(Boolean);
      const lastLine = lines[lines.length - 1] ?? "";
      const code = lastLine.slice(0, 3);
      const continuation = lastLine[3] === "-";

      if (!continuation && expectedCodes.includes(code)) {
        cleanup();
        resolve(buffer);
        return;
      }

      if (!continuation && /^\d{3}/.test(lastLine) && !expectedCodes.includes(code)) {
        cleanup();
        reject(new Error(`SMTP_ERROR expected=${expectedCodes.join(",")} response=${buffer.trim()}`));
      }
    };

    socket.on("data", onData);
    socket.on("error", onError);
  });
}

async function smtpCommand(socket: tls.TLSSocket, command: string, expectedCodes: string[]) {
  socket.write(`${command}\r\n`);
  return waitFor(socket, expectedCodes);
}

async function sendViaSmtp({ to, from, password, message }: { to: string; from: string; password: string; message: string }) {
  const socket = tls.connect({ host: SMTP_HOST, port: SMTP_PORT, servername: SMTP_HOST });

  try {
    await waitFor(socket, ["220"]);
    await smtpCommand(socket, "EHLO receiptos-base", ["250"]);
    await smtpCommand(socket, "AUTH LOGIN", ["334"]);
    await smtpCommand(socket, Buffer.from(from, "utf8").toString("base64"), ["334"]);
    await smtpCommand(socket, Buffer.from(password, "utf8").toString("base64"), ["235"]);
    await smtpCommand(socket, `MAIL FROM:<${from}>`, ["250"]);
    await smtpCommand(socket, `RCPT TO:<${to}>`, ["250", "251"]);
    await smtpCommand(socket, "DATA", ["354"]);
    socket.write(`${message}\r\n.\r\n`);
    await waitFor(socket, ["250"]);
    await smtpCommand(socket, "QUIT", ["221"]);
  } finally {
    socket.end();
  }
}

async function sendEmail(markdown: string) {
  const to = process.env.DAILY_BRIEFING_TO || "jaywisdom44@gmail.com";
  const from = process.env.DAILY_BRIEFING_FROM || process.env.SMTP_USER || to;
  const smtpUser = process.env.SMTP_USER;
  const smtpPass = process.env.SMTP_PASS;

  if (!smtpUser || !smtpPass) {
    console.log(markdown);
    console.log("\nDRY_RUN=true: SMTP_USER or SMTP_PASS missing; rendered briefing only.");
    return;
  }

  const subject = `JayOps Daily Briefing — ${new Date().toISOString().slice(0, 10)}`;
  const message = buildMimeMessage({ to, from, subject, body: markdown });

  await sendViaSmtp({ to, from: smtpUser, password: smtpPass, message });

  console.log("Renderer: PASS");
  console.log("Email delivery: PASS");
  console.log("EMAIL_DELIVERY_GREEN provider=smtp.gmail.com message_id=not_returned_by_smtp");
}

function buildEasPayload(witness: DailyBriefingWitness): EasPayload {
  if (!witness.witness_hash || !witness.replay_hash) {
    throw new Error("EAS_ATTEST_ERROR missing_witness_or_replay_hash");
  }

  return {
    witness_hash: witness.witness_hash,
    prev_witness_hash: witness.prev_witness_hash,
    replay_hash: witness.replay_hash,
    repo_commit: witness.repo_commit,
    workflow_run_id: witness.workflow_run_id,
    canonicalizer_version: witness.canonicalizer_version,
    generated_at: witness.generated_at,
    authority: false,
    truth_claim: false,
  };
}

async function attestToEas(witness: DailyBriefingWitness) {
  const schemaUid = process.env.EAS_SCHEMA_UID;
  const privateKey = process.env.EAS_ATTESTER_PRIVATE_KEY;
  const contractAddress = process.env.EAS_CONTRACT_ADDRESS;
  const rpcUrl = process.env.EAS_RPC_URL || "https://mainnet.base.org";
  const recipient = process.env.EAS_RECIPIENT || process.env.DAILY_BRIEFING_RECIPIENT_ADDRESS || "0x0000000000000000000000000000000000000000";

  if (!schemaUid || !privateKey || !contractAddress) {
    console.log("EAS_ATTEST_DRY_RUN=true: EAS_SCHEMA_UID, EAS_ATTESTER_PRIVATE_KEY, or EAS_CONTRACT_ADDRESS missing.");
    return;
  }

  const account = privateKeyToAccount(privateKey as `0x${string}`);
  const client = createWalletClient({ account, chain: base, transport: http(rpcUrl) });
  const payload = buildEasPayload(witness);
  const data = encodeAbiParameters(
    [
      { type: "string", name: "witness_hash" },
      { type: "string", name: "prev_witness_hash" },
      { type: "string", name: "replay_hash" },
      { type: "string", name: "repo_commit" },
      { type: "string", name: "workflow_run_id" },
      { type: "string", name: "canonicalizer_version" },
      { type: "string", name: "generated_at" },
      { type: "bool", name: "authority" },
      { type: "bool", name: "truth_claim" },
    ],
    [
      payload.witness_hash,
      payload.prev_witness_hash,
      payload.replay_hash,
      payload.repo_commit,
      payload.workflow_run_id,
      payload.canonicalizer_version,
      payload.generated_at,
      payload.authority,
      payload.truth_claim,
    ],
  );

  const txHash = await client.writeContract({
    address: contractAddress as `0x${string}`,
    abi: parseAbi([
      "function attest((bytes32 schema,(address recipient,uint64 expirationTime,bool revocable,bytes32 refUID,bytes data,uint256 value) data) request) payable returns (bytes32)",
    ]),
    functionName: "attest",
    args: [
      {
        schema: schemaUid as `0x${string}`,
        data: {
          recipient: recipient as `0x${string}`,
          expirationTime: 0n,
          revocable: false,
          refUID: `0x${"0".repeat(64)}`,
          data,
          value: 0n,
        },
      },
    ],
    value: 0n,
  });

  console.log(`EAS_ATTEST_SUBMITTED tx_hash=${txHash}`);
}

async function main() {
  const witness = sealWitness({
    canonicalizer_version: process.env.CANONICALIZER_VERSION || CANONICALIZER_VERSION,
    generated_at: new Date().toISOString(),
    prev_witness_hash: process.env.PREV_WITNESS_HASH || GENESIS_PREV_WITNESS_HASH,
    replay_hash: null,
    repo_commit: process.env.GITHUB_SHA || process.env.REPO_COMMIT || "missing",
    workflow_run_id: process.env.GITHUB_RUN_ID || process.env.WORKFLOW_RUN_ID || "missing",
    witness_hash: null,
    github_workflows: readJsonEnv<WorkflowWitness[]>("DAILY_BRIEFING_GITHUB_WORKFLOWS", []),
    deployments: readJsonEnv<DeploymentWitness[]>("DAILY_BRIEFING_DEPLOYMENTS", []),
    calendar: readJsonEnv<CalendarWitness[]>("DAILY_BRIEFING_CALENDAR", []),
    invariants: {
      authority: false,
      fail_closed: true,
      no_summaries_no_scores: true,
      replayable: true,
      truth_claim: false,
      witness_only: true,
    },
  });

  const markdown = renderDailyBriefing(witness);
  console.log(`WITNESS_HASH=${witness.witness_hash}`);
  console.log(`REPLAY_HASH=${witness.replay_hash}`);
  await sendEmail(markdown);
  await attestToEas(witness);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
