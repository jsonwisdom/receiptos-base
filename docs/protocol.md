# ReceiptOS Protocol

ReceiptOS is a deterministic, hash-chained receipt protocol for media generation, editing, and transformation.

Core invariants:

- Canonical JSON serialization
- SHA-256 hashing
- Deterministic event-hash
- Deterministic asset ordering
- No timestamps in hashed objects
- authority=false always explicit
- Hash chaining via prev_hash -> event_hash
- Tool-agnostic adapter interface
- Anchors optional (IPFS, EAS)

ReceiptOS Base is the canonical home for schemas, hash logic, and verification workflows.
