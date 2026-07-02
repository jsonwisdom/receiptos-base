-- Migration Review Draft: MCP Call Receipt Core v0.1
-- Issue #28 - Greenfield baseline verified
-- public schema scan result: []
-- posture: review-only until explicitly applied
-- authority=false
-- mutation=false until db push/apply

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS public.mcp_call_receipts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    call_id TEXT UNIQUE NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,

    actor TEXT,
    tool TEXT,
    project_ref TEXT,
    feature_scope TEXT DEFAULT 'database,docs',
    read_only BOOLEAN NOT NULL DEFAULT true,
    query_hash TEXT NOT NULL,
    result_hash TEXT NOT NULL,

    receipt_data JSONB NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'pending'
      CHECK (status IN ('pending', 'reviewed', 'approved', 'rejected')),

    reviewed_at TIMESTAMPTZ,
    reviewer_notes TEXT,
    reviewer_id UUID REFERENCES auth.users(id),

    metadata JSONB NOT NULL DEFAULT '{}',
    mutation BOOLEAN NOT NULL DEFAULT false,
    authority BOOLEAN NOT NULL DEFAULT false,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT mcp_call_receipts_read_only_true CHECK (read_only = true),
    CONSTRAINT mcp_call_receipts_mutation_false CHECK (mutation = false),
    CONSTRAINT mcp_call_receipts_authority_false CHECK (authority = false)
);

CREATE INDEX IF NOT EXISTS idx_mcp_receipts_call_id
  ON public.mcp_call_receipts (call_id);

CREATE INDEX IF NOT EXISTS idx_mcp_receipts_user_id
  ON public.mcp_call_receipts (user_id);

CREATE INDEX IF NOT EXISTS idx_mcp_receipts_status
  ON public.mcp_call_receipts (status);

CREATE INDEX IF NOT EXISTS idx_mcp_receipts_created
  ON public.mcp_call_receipts (created_at DESC);

ALTER TABLE public.mcp_call_receipts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users view own receipts"
ON public.mcp_call_receipts
FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

-- No broad reviewer/admin policy in v0.1.
-- Reviewer management must be added only after role table or JWT claim policy exists.

CREATE OR REPLACE FUNCTION public.update_mcp_receipts_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_mcp_receipts_updated ON public.mcp_call_receipts;

CREATE TRIGGER trg_mcp_receipts_updated
BEFORE UPDATE ON public.mcp_call_receipts
FOR EACH ROW
EXECUTE FUNCTION public.update_mcp_receipts_timestamp();

COMMENT ON TABLE public.mcp_call_receipts IS
'Review draft for ReceiptOS MCP call receipts - Issue #28 greenfield. authority=false, mutation=false.';
