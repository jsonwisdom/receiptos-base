# Quadratic Gambit Firewall — Verification

This directory is a cryptographic witness packet. It creates no authority and performs no encryption.

## Bound artifact

- Canonical bytes: `payload.canonical.json`
- SHA-256: `fbbd98cf804e11d3ac36af60eafb91f5f4fa576472c7db509af7afa646ecadbc`
- Signature algorithm: Ed25519
- Public key encoding: raw 32-byte key, Base64
- Detached signature encoding: Base64
- Signer identity: `UNBOUND_EPHEMERAL_WORK_MODE_WITNESS`
- Signer authority: `FALSE`

## Python verification

```python
import base64, hashlib
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

p = Path('.')
payload = (p / 'payload.canonical.json').read_bytes()
expected = (p / 'payload.sha256').read_text().split()[0]
assert hashlib.sha256(payload).hexdigest() == expected
public_key = Ed25519PublicKey.from_public_bytes(base64.b64decode((p / 'ed25519-public-key.base64').read_text()))
public_key.verify(base64.b64decode((p / 'payload.sig').read_text()), payload)
print('VERIFIED')
```

## Boundary

`VERIFIED` proves that the committed canonical bytes match the digest and detached signature under the committed public key. It does not prove human identity, ownership, governmental authority, legal validity, or encryption.
