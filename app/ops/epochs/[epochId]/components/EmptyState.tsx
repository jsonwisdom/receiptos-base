import type { ReactNode } from "react";

type RetryAction = () => void;

type Diff = {
  summary?: string;
  expected?: string;
  actual?: string;
};

function Panel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section style={{ border: "2px solid #ef4444", background: "#fef2f2", borderRadius: "0.75rem", padding: "1rem" }}>
      <h1>{title}</h1>
      {children}
    </section>
  );
}

export function EpochNotFound({ epochId }: { epochId: string }) {
  return (
    <Panel title="Epoch Not Found">
      <p>Epoch ID not found: <code>{epochId}</code></p>
      <p>State: <strong>NOT_FOUND</strong></p>
    </Panel>
  );
}

export function WitnessPending({ epochId, retryAction }: { epochId: string; retryAction?: RetryAction }) {
  return (
    <Panel title="Witness Pending">
      <p>Epoch ID: <code>{epochId}</code></p>
      <p>State: <strong>WITNESS_PENDING</strong></p>
      {retryAction ? <button type="button" onClick={retryAction}>Retry</button> : null}
    </Panel>
  );
}

export function DivergenceDetected({ epochId, expectedHash, actualHash, diff }: { epochId: string; expectedHash: string; actualHash: string; diff?: Diff }) {
  return (
    <Panel title="Divergence Detected">
      <p>Epoch ID: <code>{epochId}</code></p>
      <p>Expected hash: <code>{expectedHash}</code></p>
      <p>Actual hash: <code>{actualHash}</code></p>
      {diff ? <pre>{JSON.stringify(diff, null, 2)}</pre> : null}
    </Panel>
  );
}

export function ErrorNoGreen({ error, retryAction }: { error?: Error | string; retryAction?: RetryAction }) {
  return (
    <Panel title="Error No Green">
      <p>State: <strong>ERROR_NO_GREEN</strong></p>
      {error ? <pre>{typeof error === "string" ? error : error.message}</pre> : null}
      {retryAction ? <button type="button" onClick={retryAction}>Retry</button> : null}
    </Panel>
  );
}
