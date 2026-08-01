# JAYWISDOM Canonical Profile Binding v0.2.2

**Status:** `QUARANTINED_DRAFT`  
**Authority:** `FALSE`  
**Promotion:** `PROHIBITED`  
**Audit gate:** `410 OPEN`  
**Purpose:** Bind existing canonicalization rails to explicit profile identifiers without creating a new serializer.

## 1. Controlling Rule

No canonical digest is meaningful without its declared canonicalization profile.

```text
canonical_digest_identity = (
  profile_id,
  hash_algorithm,
  digest
)
```

Bare digest comparison is prohibited.

## 2. Profile Registry

### 2.1 `JAYWISDOM_NFC_RECEIPT_V1`

**Use:** Receipt packets and immutable receipt-core hashing.

**Existing rail references:**

```text
docs/canonicalization.md
receiptos/core/hash.py
tests/test_canonical.py
```

**Binding properties:**

```text
unicode_policy        = NFC_NORMALIZED
object_key_order      = LEXICOGRAPHIC_RECURSIVE
array_order           = PRESERVED
whitespace            = NONE
encoding              = UTF8_NO_BOM
number_policy         = FLOATS_REJECTED_UNLESS_LATER_PROFILE_DEFINES_THEM
hash_algorithm        = SHA256
hash_scope            = IMMUTABLE_RECEIPT_CORE
mutable_metadata      = EXCLUDED
```

NFC normalization applies before ordering and hashing. A conforming implementation must reject any object whose distinct source keys collapse to the same key after NFC normalization. Existing code is a reference rail, not proof that every profile requirement has already passed independent conformance testing.

### 2.2 `JAYWISDOM_BYTE_STRICT_EVIDENCE_V1`

**Use:** Raw evidence, observation ledgers, and byte-distinct evidentiary records.

**Existing rail references:**

```text
ep/canonical.py
spec/EVIDENCE_GRAPH.md
tests/test_canonical.py
```

**Binding properties:**

```text
unicode_policy        = BYTE_STRICT_NO_NORMALIZATION
object_key_order      = LEXICOGRAPHIC_RECURSIVE
array_order           = PRESERVED
whitespace            = NONE
encoding              = UTF8_NO_BOM
solidus_escape        = FORBIDDEN
number_policy         = INTEGER_ONLY
hash_algorithm        = SHA256
hash_scope            = DECLARED_EVIDENCE_OBJECT
```

Visually equivalent NFC and NFD strings remain distinct. No implementation may normalize, case-fold, trim, or otherwise rewrite evidence values before canonical hashing under this profile.

## 3. Comparison Rules

```text
SAME_PROFILE + SAME_ALGORITHM + SAME_DIGEST
  = byte-identical canonical output under that profile

DIFFERENT_PROFILE
  = NOT COMPARABLE

MISSING_PROFILE
  = FAIL_CLOSED

UNKNOWN_PROFILE
  = FAIL_CLOSED
```

The following operations are prohibited:

- Comparing bare hashes without profile identifiers.
- Treating equality across profiles as proof of equivalence.
- Treating inequality across profiles as proof of content difference.
- Auto-detecting a profile from serialized bytes.
- Re-labeling an existing digest under another profile.
- Silently migrating historical receipts to a new profile.

## 4. Profile Selection

A producer must declare `profile_id` before canonicalization.

```json
{
  "profile_id": "JAYWISDOM_NFC_RECEIPT_V1",
  "hash_algorithm": "sha256",
  "digest": "sha256:<64-lowercase-hex>"
}
```

Profile selection is immutable for a sealed receipt. Migration requires a new receipt that:

1. references the prior receipt;
2. declares the new profile;
3. preserves the prior digest unchanged;
4. records both canonical byte outputs when available;
5. makes no claim that cross-profile hashes are directly comparable.

## 5. Separation Doctrine

```text
NFC_RECEIPT_PROFILE   != BYTE_STRICT_EVIDENCE_PROFILE
RECEIPT_IDENTITY      != RAW_EVIDENCE_IDENTITY
NORMALIZATION         != VERIFICATION
HASH_EQUALITY         != TRUTH
PROFILE_BINDING       != AUTHORITY
```

Receipt canonicalization may normalize identity-bearing text for deterministic receipt processing. Raw-evidence canonicalization must preserve byte-distinct Unicode representations. Neither profile creates factual correctness or legal authority.

## 6. Conformance Gate

No profile may be promoted until all applicable conditions pass:

```text
REFERENCE_IMPLEMENTATION_A_BYTES == REFERENCE_IMPLEMENTATION_B_BYTES
REFERENCE_IMPLEMENTATION_A_SHA256 == REFERENCE_IMPLEMENTATION_B_SHA256
NEGATIVE_VECTORS_FAIL_IDENTICALLY
NORMALIZED_KEY_COLLISIONS_FAIL_CLOSED
UNPAIRED_SURROGATES_FAIL_CLOSED
PROFILE_ID_BOUND_IN_RECEIPT
AUDIT_410 == CLOSED
```

## 7. Non-Mutation Boundary

This document:

- creates no serializer;
- changes no existing serializer;
- changes no historical receipt or digest;
- activates no signing, authorization, release, or production gate;
- grants no authority to a token, wallet, attestation, repository, or operator;
- does not close Audit #410.

## 8. Locked Posture

```text
CANONICAL_DIALECT_REALITY     = LOCKED
PROFILE_NAMES                 = LOCKED
CROSS_PROFILE_COMPARISON      = PROHIBITED
NEW_SERIALIZER                = NONE
HISTORICAL_REHASH             = NONE
AUTHORITY                     = FALSE
PROMOTION                     = PROHIBITED
AUDIT_410                     = OPEN
STATUS                        = QUARANTINED_DRAFT
```

Proof may be replayed. Profiles may not be collapsed. ⚙️
