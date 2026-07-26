# RP-005 Verification Bundle Checklist

**Corpus commit (declared):** `964470053d61abb60f339d67a9f1ada60ad54472`  
**Expected root hash:** `3811d6961928668b7b780ab3c248e66dd318b23c66c2ba4b1d2dc7d037de722b`  
**State until complete:** `WAITING_FOR_RECEIPTS` · **Promotion:** BLOCKED

Use this checklist for every Team A / Team B `VerificationResult` and for the CE-2 comparison. Do not promote until every required box is checked against actual receipt artifacts.

---

## 0. Pre-conditions

- [ ] Receipt references repository `jsonwisdom/receiptos-base`
- [ ] Receipt `commit` (or equivalent) equals `964470053d61abb60f339d67a9f1ada60ad54472`
- [ ] Receipt declares corpus path `golden-corpus/rp-005/`
- [ ] Receipt declares profile `A` / standard `RP-005/v1.0`

---

## 1. Receipt integrity (per team)

Required fields present in each VerificationResult:

- [ ] `team` — `"A"` or `"B"`
- [ ] `commit` — full SHA
- [ ] `corpus_root_hash` — 64-char lowercase hex
- [ ] `vectors_executed` — integer
- [ ] `pass_count` — integer
- [ ] `fail_count` — integer
- [ ] `exit_code_distribution` — map of exit code → count
- [ ] `report_hash` — SHA-256 of the canonical report bytes (for CE-2)
- [ ] `timestamp` or `generated_at` — ISO-8601
- [ ] `harness_id` / `harness_version` — implementation identity

Integrity gate: **FAIL** if any required field is missing or commit mismatches target.

---

## 2. Root hash binding

- [ ] Team A `corpus_root_hash` == `3811d6961928668b7b780ab3c248e66dd318b23c66c2ba4b1d2dc7d037de722b`
- [ ] Team B `corpus_root_hash` == `3811d6961928668b7b780ab3c248e66dd318b23c66c2ba4b1d2dc7d037de722b`
- [ ] Team A hash == Team B hash

Root-hash gate: **FAIL** if either team diverges from expected or from each other.

---

## 3. Harness outcome

### Vector coverage

- [ ] `vectors_executed` covers all sealed family cases (minimum 4 for v1.0.0 scaffold)
- [ ] Every path under `valid/`, `invalid/`, `edge/`, `regression/` with `input.json` + `expected.json` was executed

### Family expectations

- [ ] **valid/** — all PASS, exit code `0`
- [ ] **invalid/** — expected FAIL, exit code `65`
- [ ] **edge/** — expected FAIL where specified, exit code `65`
- [ ] **regression/** — PASS, exit code `0`

### Counts

- [ ] `pass_count` + `fail_count` == `vectors_executed`
- [ ] Exit code `65` count matches number of invalid + rejecting edge vectors
- [ ] Exit code `0` count matches valid + accepting regression vectors

### Canonicalization

- [ ] Profile A / JCS key order verified (or harness asserts equivalent)
- [ ] Repeated run within same team yields identical `corpus_root_hash`

Outcome gate: **FAIL** if family exit codes or counts disagree with sealed `expected.json`.

---

## 4. CE-2 bit-identical reportHash comparison

- [ ] Team A `report_hash` present
- [ ] Team B `report_hash` present
- [ ] `report_hash` algorithm is SHA-256 over canonical report serialization
- [ ] Team A `report_hash` **byte-for-byte equals** Team B `report_hash`

| Condition | Result |
|-----------|--------|
| Root hashes match expected **and** CE-2 `report_hash` identical | Deterministic replay confirmed |
| Root hashes match, `report_hash` differs | Corpus deterministic; report serialization differs — investigate report encoding |
| Root hashes differ | Replay divergence — do not promote |
| Missing / incomplete receipts | Insufficient evidence — remain WAITING_FOR_RECEIPTS |

CE-2 gate: **FAIL** if hashes differ or either side is absent.

---

## 5. Promotion decision

Promotion to sealed / verified is allowed **only** when:

1. Sections 0–3 pass for **both** Team A and Team B  
2. Section 4 (CE-2) passes  
3. No unresolved diagnostic mismatches remain  

Otherwise:

- **State:** `WAITING_FOR_RECEIPTS` or `REPLAY_DIVERGENCE`  
- **Promotion:** BLOCKED  

---

## 6. Artifact drop locations (suggested)

```
golden-corpus/rp-005/receipts/
  team-a-verification-result.json
  team-b-verification-result.json
  ce-2-report-hash-comparison.json
```

Filenames may vary; content must satisfy sections 1–4.

---

## 7. Minimal VerificationResult schema (informative)

```json
{
  "team": "A",
  "commit": "964470053d61abb60f339d67a9f1ada60ad54472",
  "corpus_path": "golden-corpus/rp-005",
  "profile": "A",
  "standard": "RP-005/v1.0",
  "corpus_root_hash": "3811d6961928668b7b780ab3c248e66dd318b23c66c2ba4b1d2dc7d037de722b",
  "vectors_executed": 4,
  "pass_count": 2,
  "fail_count": 2,
  "exit_code_distribution": {
    "0": 2,
    "65": 2
  },
  "report_hash": "<sha256-of-canonical-report>",
  "harness_id": "<implementation>",
  "harness_version": "<semver>",
  "generated_at": "<ISO-8601>"
}
```

Keys sorted (Profile A) when the receipt itself is sealed as JCS JSON.
