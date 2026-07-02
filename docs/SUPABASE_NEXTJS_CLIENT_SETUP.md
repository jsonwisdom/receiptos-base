# Supabase Next.js Client Setup

This document records the safe application-side Supabase setup for ReceiptOS.

## Boundary

The application client uses publishable values only.

Do not commit service-role keys. The service-role key is only for trusted server-side environments or GitHub Actions secrets.

## Required local app variables

Create `.env.local` locally from `.env.example`:

```bash
cp .env.example .env.local
```

Fill only local values in `.env.local`:

```txt
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=
```

## Required GitHub Actions secret

For W031 archival upload workflow:

```txt
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
```

Set these under:

```txt
GitHub repo → Settings → Secrets and variables → Actions → New repository secret
```

## Storage target

```txt
bucket: gpp-cards
prefix: first-printing/W031_Reputation_Rascals
```

## Governance semantics

Until production logs prove upload + manifest commit:

```txt
authority=false
truthClaim=false
SUPADRIVE_ARCHIVED=false
```

A successful upload may establish archival evidence, but it does not turn the workflow into a truth adjudicator.

## Next production check

After secrets and bucket exist:

```bash
gh workflow run gpp-render-wave.yml \
  -R jsonwisdom/receiptos-base \
  -f lane=production \
  -f wave=W031 \
  -f production_confirm=true
```

Then verify logs for:

```txt
Supabase production secrets present
SUPABASE_UPLOAD_COMPLETE=true
SUPADRIVE_ARCHIVED_PENDING_ATTESTATION=true
```
