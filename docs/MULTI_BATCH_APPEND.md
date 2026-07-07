# Multi-Batch Append

Issue: #38

## Result

The audit log now has two entries.

## Entries

1. `batch-root-entry-000001`
   - root: `sha256:6ffc207fe8fb31296c27fc1457e233af771dca3800ce299cd262777fef790dad`
   - leaf count: 2

2. `batch-root-entry-000002`
   - root: `sha256:7107ad37be56fbd8872463c911d650d526f821c371986fd06dddf85378ecaaaa`
   - leaf count: 1
   - manifest: `lattice/fixtures/batch-root-manifest-rp001-only.example.json`
   - manifest hash: `sha256:145ec52bff0ed0bb2a7c9cab1deefe3b1e7b9c9aa39fafbf5d90bedc91f4e50e`

## Commands

```bash
python audit/verify_log_continuity.py --log audit/logs/batch-roots.jsonl --repo-root .
```

```bash
python audit/export_verified_roots.py --log audit/logs/batch-roots.jsonl --repo-root .
```

## Fixtures

- `audit/fixtures/batch-root-audit-verify-002.example.json`
- `audit/fixtures/verified-root-export-002.example.json`

## Boundary

Sequence is storage order only.

No extra meaning is added.
