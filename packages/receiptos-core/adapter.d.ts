export interface ReceiptOSAdapter {
  beforeStage(input: {
    stage_id: string;
    assets: Array<{
      asset_id: string;
      hash: string;
      media_type: string;
      uri?: string;
    }>;
    tool_chain: Array<{
      tool_id: string;
      version: string;
      parameters?: Record<string, unknown>;
    }>;
  }): Promise<void>;

  afterStage(output: {
    stage_id: string;
    assets: Array<{
      asset_id: string;
      hash: string;
      media_type: string;
      uri?: string;
    }>;
  }): Promise<void>;
}
