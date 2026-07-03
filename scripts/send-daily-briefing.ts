import tls from "node:tls";

const SMTP_HOST = "smtp.gmail.com";
const SMTP_PORT = 465;

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
  generated_at: string;
  replay_hash?: string | null;
  github_workflows: WorkflowWitness[];
  deployments: DeploymentWitness[];
  calendar: CalendarWitness[];
  invariants: {
    witness_only: true;
    fail_closed: true;
    replayable: true;
    no_summaries_no_scores: true;
    authority: false;
    truth_claim: false;
  };
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
Replay hash: ${witness.replay_hash ?? "missing"}

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

async function main() {
  const witness: DailyBriefingWitness = {
    generated_at: new Date().toISOString(),
    replay_hash: process.env.DAILY_BRIEFING_REPLAY_HASH || null,
    github_workflows: readJsonEnv<WorkflowWitness[]>("DAILY_BRIEFING_GITHUB_WORKFLOWS", []),
    deployments: readJsonEnv<DeploymentWitness[]>("DAILY_BRIEFING_DEPLOYMENTS", []),
    calendar: readJsonEnv<CalendarWitness[]>("DAILY_BRIEFING_CALENDAR", []),
    invariants: {
      witness_only: true,
      fail_closed: true,
      replayable: true,
      no_summaries_no_scores: true,
      authority: false,
      truth_claim: false,
    },
  };

  const markdown = renderDailyBriefing(witness);
  await sendEmail(markdown);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
