# Cloud Shell Intake Agent Spec v0.1

Status: scaffold / no execution logic  
Issue: #119  
Invariant: `authority=false`

## Purpose

Define a future read-only Cloud Shell / `gcloud` intake rail that can produce raw evidence packets for ReceiptOS without mutating cloud resources.

This spec preserves the future production target only. It does not solve the prior Google Cloud access incident and does not authorize mutation.

## Allowed Command Shape

Commands must be read-only and must emit JSON:

```text
gcloud ... --format=json
```

Initial allowlist:

```yaml
allowed_commands:
  - gcloud projects describe [PROJECT] --format=json
  - gcloud projects get-iam-policy [PROJECT] --format=json
  - gcloud asset search-all-resources --format=json
```

## Forbidden Commands

```yaml
forbidden:
  - gcloud auth login
  - gcloud config set
  - gcloud deploy
  - gcloud services enable
  - gcloud iam service-accounts keys create
  - gcloud iam service-accounts keys delete
  - gcloud iam service-accounts disable
  - any create/update/delete mutation
  - any credential creation
  - any key operation
```

## Output Pipeline

```text
gcloud ... --format=json
  → stdout capture
  → IntakeAgent
  → raw_evidence packet
  → CAPTURED
  → ReceiptOS state machine
```

## Bedrock Rule

No browser dependency assumption. No credentials created. No keys. No mutation. No fake green.
