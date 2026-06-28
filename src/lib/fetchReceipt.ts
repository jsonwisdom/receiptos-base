import type { ReceiptPacket } from "./verifyReceipt";

export async function fetchReceiptFromCID(cid: string): Promise<ReceiptPacket> {
  const clean = cid.replace("ipfs://", "").trim();
  const url = `https://ipfs.io/ipfs/${clean}`;

  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`IPFS fetch failed: ${res.status}`);
  }

  return await res.json();
}
