# Root Subscription Manifest

Issue: #38

## Purpose

Read-only feed of verified batch roots.

## Command

```bash
python audit/subscription_manifest.py --log audit/logs/batch-roots.jsonl --repo-root .
```

## Fixture

```text
audit/fixtures/root-subscription-manifest-002.example.json
```

## Boundary

Read-only. Verifier-gated. Storage sequence only.

No extra meaning is added.

## Next

Timeline semantics stay deferred until this feed is externally stable.