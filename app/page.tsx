export default function ReceiptOSBaseStatus() {
  const rows = [
    ["Architecture", "AL governance/spec → receiptos-base implementation → JOY runtime/client"],
    ["Foundation", "PR #105 merged: AL interface v0.1 + deterministic replay surface"],
    ["Current JOY contract", "PR #106 open: client/runtime contract only"],
    ["Base rail", "EAS bootstrap anchor recorded"],
    ["authority", "false"],
    ["verifiedReplay", "false"],
    ["loadVerified", "false"],
    ["classification", "BOOTSTRAP / not LOAD_VERIFIED"],
  ];

  return (
    <main style={{ minHeight: "100vh", background: "#05070a", color: "#d7f9ff", fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace", padding: "2rem" }}>
      <section style={{ maxWidth: 980, margin: "0 auto", display: "grid", gap: "1.5rem" }}>
        <div>
          <p style={{ color: "#67e8f9", letterSpacing: "0.16em", textTransform: "uppercase" }}>ReceiptOS Base</p>
          <h1 style={{ fontSize: "2.5rem", margin: "0 0 0.5rem" }}>Base-native receipt infrastructure</h1>
          <p style={{ color: "#9ca3af", lineHeight: 1.6 }}>
            Governance stays in AL. Base-native receipt implementation lives here. JOY consumes the public runtime contract.
            No verified replay or LOAD_VERIFIED claim is made by this page.
          </p>
        </div>

        <section style={{ border: "1px solid #155e75", borderRadius: 16, padding: "1rem", background: "#07131c" }}>
          <h2 style={{ marginTop: 0 }}>Current public status</h2>
          <div style={{ display: "grid", gap: "0.75rem" }}>
            {rows.map(([label, value]) => (
              <div key={label} style={{ display: "grid", gridTemplateColumns: "minmax(180px, 0.35fr) 1fr", gap: "1rem", borderBottom: "1px solid #12313f", paddingBottom: "0.75rem" }}>
                <strong style={{ color: "#67e8f9" }}>{label}</strong>
                <span>{value}</span>
              </div>
            ))}
          </div>
        </section>

        <section style={{ border: "1px solid #7f1d1d", borderRadius: 16, padding: "1rem", background: "#160b0b" }}>
          <h2 style={{ marginTop: 0, color: "#fca5a5" }}>Doctrine guard</h2>
          <p style={{ color: "#fecaca", lineHeight: 1.6 }}>
            Until a real <code>LOAD_VERIFICATION_WITNESS_V0_1</code> exists with <code>gate_result.status === "LOAD_VERIFIED"</code>,
            the only admissible public state is <strong>BOOTSTRAP / not LOAD_VERIFIED</strong>.
          </p>
          <ul style={{ color: "#fecaca", lineHeight: 1.8 }}>
            <li>No verified replay claim.</li>
            <li>No LOAD_VERIFIED badge.</li>
            <li>No synthetic verification pass.</li>
            <li>No fake green.</li>
          </ul>
        </section>

        <section style={{ border: "1px solid #164e63", borderRadius: 16, padding: "1rem", background: "#08111a" }}>
          <h2 style={{ marginTop: 0 }}>Next required evidence</h2>
          <p style={{ color: "#9ca3af", lineHeight: 1.6 }}>
            Run the real JOY harness, emit <code>/receipts/{"{run_id}"}.json</code>, and audit the witness before promoting any replay status.
          </p>
        </section>
      </section>
    </main>
  );
}
