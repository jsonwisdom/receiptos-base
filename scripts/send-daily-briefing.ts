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

async function sendEmail(markdown: string) {
  const endpoint = process.env.DAILY_BRIEFING_EMAIL_ENDPOINT;
  const token = process.env.DAILY_BRIEFING_EMAIL_TOKEN;
  const to = process.env.DAILY_BRIEFING_TO;

  if (!endpoint || !token || !to) {
    console.log(markdown);
    console.log("\nDRY_RUN=true: email env vars missing; rendered briefing only.");
    return;
  }

  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      to,
      subject: `JayOps Daily Briefing — ${new Date().toISOString().slice(0, 10)}`,
      markdown,
    }),
  });

  if (!response.ok) {
    throw new Error(`Email send failed: ${response.status} ${response.statusText}`);
  }
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
