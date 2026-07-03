"use client";

import { useMemo, useState } from "react";
import { BrowserProvider } from "ethers";

const EXPECTED_SIGNER = "0xA380552a27b0a5a2874Ea7AA52CAC09f542002E8";

const MESSAGE = `subject: jaywisdom.base.eth
ens: jaywisdom.eth
wallet: 0xA380552a27b0a5a2874Ea7AA52CAC09f542002E8
service: ReceiptOS Meme Court Frame MVP
endpoint: https://receiptos-frame-mvp.vercel.app
issue: jsonwisdom/receiptos-base#57
deployment_receipt: gcp-cloud-build:e0e45d99-ab21-49be-b675-bee556623283
court_state: FRAME_MVP_DEPLOYMENT_RECEIPT_VERIFIED
signature_gate: SIGNATURE_BUNDLE_PENDING
authority: false
truth_claim: false
`;

type EthereumProvider = {
  request: (args: { method: string; params?: unknown[] }) => Promise<unknown>;
};

declare global {
  interface Window {
    ethereum?: EthereumProvider;
  }
}

export default function SignPage() {
  const [account, setAccount] = useState<string>("");
  const [signature, setSignature] = useState<string>("");
  const [error, setError] = useState<string>("");

  const sigJson = useMemo(() => {
    if (!signature || !account) return "";
    return JSON.stringify(
      {
        schema: "RECEIPTOS_IDENTITY_BINDING_SIG_V1",
        address: account,
        signer: account,
        method: "personal_sign",
        signed_file: "provenance/identity-binding/jaywisdom-identity-binding.txt",
        msg: MESSAGE,
        signature,
        sig: signature,
        version: "2",
        authority: false,
        truth_claim: false,
      },
      null,
      2,
    );
  }, [account, signature]);

  async function connectAndSign() {
    setError("");
    setSignature("");

    if (!window.ethereum) {
      setError("No wallet provider found. Open this page inside Base App, MetaMask, or another EVM wallet browser.");
      return;
    }

    const provider = new BrowserProvider(window.ethereum as any);
    await provider.send("eth_requestAccounts", []);
    const signer = await provider.getSigner();
    const address = await signer.getAddress();
    setAccount(address);

    if (address.toLowerCase() !== EXPECTED_SIGNER.toLowerCase()) {
      setError(`Wrong wallet connected. Expected ${EXPECTED_SIGNER}, got ${address}. Switch to jaywisdom.base.eth / 0xA380...02E8 and try again.`);
      return;
    }

    const sig = await signer.signMessage(MESSAGE);
    setSignature(sig);
  }

  async function copyOutput() {
    if (!sigJson) return;
    await navigator.clipboard.writeText(sigJson);
  }

  return (
    <main style={{ fontFamily: "system-ui, sans-serif", padding: 20, maxWidth: 880, margin: "0 auto" }}>
      <h1>ReceiptOS Sign</h1>
      <p>Connect <strong>jaywisdom.base.eth</strong>, sign the identity binding, then copy the public signature JSON.</p>

      <section style={{ border: "1px solid #ddd", borderRadius: 12, padding: 16, marginBottom: 16 }}>
        <p><strong>Expected signer</strong></p>
        <code style={{ overflowWrap: "anywhere" }}>{EXPECTED_SIGNER}</code>
      </section>

      <section style={{ border: "1px solid #ddd", borderRadius: 12, padding: 16, marginBottom: 16 }}>
        <p><strong>Message to sign</strong></p>
        <pre style={{ whiteSpace: "pre-wrap", overflowWrap: "anywhere" }}>{MESSAGE}</pre>
      </section>

      <button onClick={connectAndSign} style={{ fontSize: 18, padding: "14px 18px", borderRadius: 10, border: 0, cursor: "pointer" }}>
        Connect Wallet + Sign Message
      </button>

      {account ? (
        <p style={{ overflowWrap: "anywhere" }}><strong>Connected:</strong> {account}</p>
      ) : null}

      {error ? (
        <p style={{ color: "crimson", overflowWrap: "anywhere" }}><strong>{error}</strong></p>
      ) : null}

      {sigJson ? (
        <section style={{ border: "1px solid #ddd", borderRadius: 12, padding: 16, marginTop: 16 }}>
          <p><strong>Public signature JSON</strong></p>
          <pre style={{ whiteSpace: "pre-wrap", overflowWrap: "anywhere" }}>{sigJson}</pre>
          <button onClick={copyOutput} style={{ fontSize: 16, padding: "10px 14px", borderRadius: 10, border: 0, cursor: "pointer" }}>
            Copy Signature JSON
          </button>
        </section>
      ) : null}

      <p style={{ marginTop: 24, color: "#666" }}>No private keys. No transaction. This only creates public EIP-191 signature evidence. authority=false, truth_claim=false.</p>
    </main>
  );
}
