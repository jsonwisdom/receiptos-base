# Anchor Negative Fixtures

Issue: #39

## Positive

```bash
python audit/validate_subscription_feed.py audit/fixtures/root-subscription-anchor-readiness.example.json
```

## Negative

```bash
python audit/validate_subscription_feed.py audit/fixtures/negative-anchor-wrong-format.example.json
```

```bash
python audit/validate_subscription_feed.py audit/fixtures/negative-anchor-wrong-semantics.example.json
```

```bash
python audit/validate_subscription_feed.py audit/fixtures/negative-anchor-extra-field.example.json
```

## Expected failures

```text
audit/fixtures/negative-anchor-expected-failures.example.json
```

## Boundary

Only storage-time anchors pass.
