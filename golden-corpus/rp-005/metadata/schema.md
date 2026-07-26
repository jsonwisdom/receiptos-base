# RP-005 Schema

Profile: A (JCS Canonical JSON, UTF-8, LF only, sorted keys)

## Manifest

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string | yes | Corpus identifier |
| profile | string | yes | Canonicalization profile |
| root_hash | string | yes | Normative root hash binding |
| vectors | string[] | yes | Relative paths to vector files |
| version | string | yes | Corpus version |

## Vectors

Each vector file is a single JCS-canonical JSON object.
