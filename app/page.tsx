const publicUrl = process.env.NEXT_PUBLIC_URL || "https://receiptos-frame.vercel.app";

export async function generateMetadata() {
  const frame = {
    version: "vNext",
    image: `${publicUrl}/og/court-room.png`,
    buttons: [
      {
        label: "Verify Receipt",
        action: "post",
      },
      {
        label: "View Case",
        action: "link",
        target: "https://github.com/jsonwisdom/receiptos-base/issues/57",
      },
    ],
    input: {
      text: "Enter EAS UID",
    },
    postUrl: `${publicUrl}/api/frame`,
  };

  return {
    title: "ReceiptOS Court Frame",
    description: "Witness-only receipt verification frame. authority=false, truth_claim=false.",
    openGraph: {
      title: "ReceiptOS Court Frame",
      description: "No receipt, no authority.",
      images: [`${publicUrl}/og/court-room.png`],
    },
    other: {
      "fc:frame": JSON.stringify(frame),
    },
  };
}

export default function Page() {
  return (
    <main style={{ fontFamily: "system-ui, sans-serif", padding: "2rem" }}>
      <h1>ReceiptOS Court Frame</h1>
      <p>Court is in session.</p>
      <pre>
        {JSON.stringify(
          {
            status: "FRAME_MVP_PENDING_DEPLOYMENT",
            verdict: "WITNESS_ONLY",
            authority: false,
            truth_claim: false,
          },
          null,
          2,
        )}
      </pre>
    </main>
  );
}
