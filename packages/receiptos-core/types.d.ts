export interface ReceiptOSReceiptV0_1 {
  schema: "ReceiptOSReceiptV0_1";
  version: "0.1";
  receipt_id: string;
  prev_hash: string;
  event_hash: string;
  algorithm: "sha256";
  authority: false;
  stages: Array<{
    stage_id: string;
    before: {
      assets: Array<ReceiptOSAsset>;
      tool_chain: Array<ReceiptOSTool>;
    };
    after: {
      assets: Array<ReceiptOSAsset>;
    };
  }>;
  anchors?: {
    ipfs_cid?: string;
    eas_uid?: string;
  };
  metadata?: Record<string, unknown>;
}

export interface ReceiptOSAsset {
  asset_id: string;
  hash: string;
  media_type: string;
  uri?: string;
}

export interface ReceiptOSTool {
  tool_id: string;
  version: string;
  parameters?: Record<string, unknown>;
}
