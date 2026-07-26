# RP-005 Schema

Profile: A (JCS Canonical JSON, UTF-8, LF only, sorted keys)
Standard: RP-005/v1.0

## Root Manifest

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | yes | Corpus identifier |
| profile | string | yes | Canonicalization profile |
| root_hash | string | yes | SHA-256 of sealed corpus |
| families | string[] | yes | Classified family names |
| vectors | string[] | yes | Relative paths to expected.json |
| standard | string | yes | RP-005/v1.0 |
| version | string | yes | Corpus version |

## Vector Layout

```
{family}/{vector-id}/
  input.json
  expected.json
```

## Expected Object

| Field | Type | Notes |
|-------|------|-------|
| valid | bool | Pass/fail |
| exit_code | int | 0 success; 65 rejection |
| reason | string | Diagnostic code |
| family | string | valid\|invalid\|edge\|regression |
| vector | string | Case id |
| failed_field | string\|null | For invalid/edge |
