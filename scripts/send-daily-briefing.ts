type WorkflowWitness = {
  repo: string;
  workflow: string;
  status: string;
  conclusion?: string | null;
  run_url?: string | null;
  timestamp?: string | null;
};

type CalendarWitness = {
  title: string;
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
      const url = item.url ? `[open](${item.url})` : "missing";
      return `| ${item.title} | ${item.start} | ${item.end ?? "missing"} | ${url} |`;
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

function base64UrlEncode(value: string): string {
  return Buffer.from(value, "utf8").toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function buildMimeMessage({ to, from, subject, body }: { to: string; from: string; subject: string; body: string }): string {
  const lines = [
    `From: ${from}`,
    `To: ${to}`,
    `Subject: ${subject}`,
    "MIME-Version: 1.0",
    'Content-Type: text/plain; charset="UTF-8"',
    "Content-Transfer-Encoding: 8bit",
    "",
    body,
  ];

  return base64UrlEncode(lines.join("\r\n"));
}

async function getGmailAccessToken() {
  const clientId = process.env.GMAIL_CLIENT_ID;
  const clientSecret = process.env.GMAIL_CLIENT_SECRET;
  const refreshToken = process.env.GMAIL_REFRESH_TOKEN;

  if (!clientId || !clientSecret || !refreshToken) {
    return null;
  }

  const response = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      refresh_token: refreshToken,
      grant_type: "refresh_token",
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`EMAIL_DELIVERY_ERROR gmail_token ${response.status} ${response.statusText}: ${errorText}`);
  }

  const data = (await response.json()) as { access_token?: string };
  if (!data.access_token) {
    throw new Error("EMAIL_DELIVERY_ERROR gmail_token missing access_token");
  }

  return data.access_token;
}

async function sendEmail(markdown: string) {
  const to = process.env.DAILY_BRIEFING_TO;

  if (!to) {
    console.log(markdown);
    console.log("\nDRY_RUN=true: DAILY_BRIEFING_TO missing; rendered briefing only.");
    return;
  }

  const accessToken = await getGmailAccessToken();

  if (!accessToken) {
    console.log(markdown);
    console.log("\nDRY_RUN=true: Gmail OAuth env vars missing; rendered briefing only.");
    return;
  }

  const from = process.env.DAILY_BRIEFING_FROM || to;
  const subject = `JayOps Daily Briefing — ${new Date().toISOString().slice(0, 10)}`;
  const raw = buildMimeMessage({ to, from, subject, body: markdown });

  const response = await fetch("https://gmail.googleapis.com/gmail/v1/users/me/messages/send", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ raw }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`EMAIL_DELIVERY_ERROR gmail_send ${response.status} ${response.statusText}: ${errorText}`);
  }

  const result = (await response.json()) as { id?: string; threadId?: string };
  console.log("Renderer: PASS");
  console.log("Email delivery: PASS");
  console.log(`EMAIL_DELIVERY_GREEN gmail_message_id=${result.id ?? "missing"} thread_id=${result.threadId ?? "missing"}`);
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
