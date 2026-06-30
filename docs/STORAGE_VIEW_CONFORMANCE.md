# Storage View Conformance

Issue: #40

## Fixture generator

```bash
python audit/generate_storage_view_fixture.py audit/fixtures/root-subscription-anchor-readiness.example.json audit/fixtures/storage-time-sorted-view.generated.json
```

## Matrix

```bash
python audit/storage_view_conformance_matrix.py --repo-root .
```

## Coverage

- positive validated storage anchor feed
- negative bad timestamp feed
- negative wrong anchor semantics feed

## Boundary

Storage-time view only.

No event-time order is added.
