# EAS Attest Lock v1

Status: `EAS_ATTEST_LOCK_V1_READY`

This membrane anchors each sealed Daily Briefing witness to Base EAS after the witness hash and replay hash are computed.

## Schema

Permanent schema:

```txt
ReceiptOS Witness Lock v1
```

EASScan schema number observed during setup:

```txt
#1650
```

The workflow requires the full schema UID as a secret:

```txt
EAS_SCHEMA_UID=<0x...>
```

## Attestation fields

The EAS data payload is ABI-encoded in this order:

```txt
witness_hash string
prev_witness_hash string
replay_hash string
repo_commit string
workflow_run_id string
canonicalizer_version string
generated_at string
authority bool
truth_claim bool
```

## Hash rules

The script computes:

```txt
replay_hash = sha256(canonical witness object with replay_hash:null and witness_hash:null)
witness_hash = sha256(canonical witness object with replay_hash filled and witness_hash:null)
```

The final email includes both hashes.

## Required secrets for EAS activation

SMTP remains the email transport lane:

```txt
SMTP_USER
SMTP_PASS
```

EAS anchor activation requires:

```txt
EAS_SCHEMA_UID
EAS_CONTRACT_ADDRESS
EAS_ATTESTER_PRIVATE_KEY
```

Optional:

```txt
EAS_RPC_URL=https://mainnet.base.org
EAS_RECIPIENT=<recipient address>
```

If any required EAS secret is missing, the workflow does not fail; it emits:

```txt
EAS_ATTEST_DRY_RUN=true
```

This preserves daily email delivery while making the EAS rail explicitly gated.

## Success marker

A submitted EAS transaction emits:

```txt
EAS_ATTEST_SUBMITTED tx_hash=<0x...>
```

## Invariants

```txt
authority=false
truth_claim=false
witness_only=true
```

EAS proves existence, signer, timestamp, and data binding. It does not prove truth.
