type ClaimBadgeProps = {
  claimStatus?: string;
  truthClaim?: boolean;
};

export function ClaimBadge({ claimStatus, truthClaim }: ClaimBadgeProps) {
  const allowed = claimStatus === "UNPROMOTED" && truthClaim === false;

  if (!allowed) {
    return (
      <div className="rounded-lg border border-red-500 bg-red-50 p-4 font-mono">
        🔒 Protocol violation — claim promotion blocked.
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-amber-500 bg-amber-50 p-4 font-mono">
      ⚖️ CLAIM_UNPROMOTED — evidence may be replayed, not promoted to truth.
    </div>
  );
}
