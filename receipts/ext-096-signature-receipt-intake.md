# EXT-096 — Signature Receipt Intake

Status: PENDING_EXTERNAL_SIGN

Payload path:

```text
receipts/ext-096-signer-payload.jcs
```

Required real fields before verification:

```text
payload_hash
signer_fid
signature_bytes
```

Verification method:

```text
farcaster_account_association
```

Blocked statuses:

```text
SIGNED
CRYPTOGREEN
```

Block reason:

```text
This intake file contains no real externally produced signer evidence.
```

Boundary:

```text
authority=false
truth_claim=false
```

Do not mark this receipt SIGNED until a real external signature over the JCS payload is produced and verified.
