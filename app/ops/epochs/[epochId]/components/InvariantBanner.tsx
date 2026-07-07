import type { InvariantState, Invariants } from "./types";

const stateStyles: Record<InvariantState, { border: string; background: string }> = {
  PASS: { border: "#22c55e", background: "#f0fdf4" },
  WITNESS_PENDING: { border: "#eab308", background: "#fefce8" },
  DIVERGENCE_DETECTED: { border: "#ef4444", background: "#fef2f2" },
  ERROR_NO_GREEN: { border: "#ef4444", background: "#fef2f2" },
};

export function InvariantBanner({ state, invariants }: { state: InvariantState; invariants: Invariants }) {
  const style = stateStyles[state];

  return (
    <section
      aria-label="Epoch invariants"
      style={{
        position: "sticky",
        top: 0,
        zIndex: 10,
        border: `2px solid ${style.border}`,
        background: style.background,
        borderRadius: "0.75rem",
        padding: "1rem",
        marginBottom: "1rem",
      }}
    >
      <strong>Invariant State: {state}</strong>
      <ul style={{ display: "grid", gap: "0.35rem", margin: "0.75rem 0 0", paddingLeft: "1.25rem" }}>
        {Object.entries(invariants).map(([key, value]) => (
          <li key={key}>
            <code>{key}</code>: <strong>{String(value)}</strong>
          </li>
        ))}
      </ul>
    </section>
  );
}
