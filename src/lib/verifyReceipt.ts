import { keccak256, toBytes } from "viem";

export type ReceiptPacket = {
  receipt_id: string;
  observer: `0x${string}`;
  basename: string;
  cid: string;
  state_root: string;
  git_commit: string;
  eas_uid?: string;
  tx_hash?: string;
  created_at: string;
  authority: false;
};

export type VerifyResult = {
  status: "PASS" | "FAIL" | "INCOMPLETE";
  checks: {
    cid_present: boolean;
    state_root_present: boolean;
    git_commit_present: boolean;
    authority_false: boolean;
    receipt_id_matches: boolean;
  };
  computed_receipt_id: string;
};

export function computeReceiptId(receipt: Omit<ReceiptPacket, "receipt_id">) {
  const canonical = JSON.stringify({
    observer: receipt.observer.toLowerCase(),
    basename: receipt.basename,
    cid: receipt.cid,
    state_root: receipt.state_root,
    git_commit: receipt.git_commit,
    eas_uid: receipt.eas_uid ?? "",
    tx_hash: receipt.tx_hash ?? "",
    created_at: receipt.created_at,
    authority: false,
  });

  return keccak256(toBytes(canonical));
}

export function verifyReceipt(receipt: ReceiptPacket): VerifyResult {
  const computed = computeReceiptId({
    observer: receipt.observer,
    basename: receipt.basename,
    cid: receipt.cid,
    state_root: receipt.state_root,
    git_commit: receipt.git_commit,
    eas_uid: receipt.eas_uid,
    tx_hash: receipt.tx_hash,
    created_at: receipt.created_at,
    authority: false,
  });

  const checks = {
    cid_present: Boolean(receipt.cid),
    state_root_present: Boolean(receipt.state_root),
    git_commit_present: Boolean(receipt.git_commit),
    authority_false: receipt.authority === false,
    receipt_id_matches: receipt.receipt_id === computed,
  };

  const passed = Object.values(checks).every(Boolean);

  return {
    status: passed ? "PASS" : "FAIL",
    checks,
    computed_receipt_id: computed,
  };
}
