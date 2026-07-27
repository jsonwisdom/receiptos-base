# ARC

ARC is the local architecture and repository-contract boundary for
`receiptos-base`.

## Discovery

The canonical discovery artifact is:

- `ARC/manifest.json`

Its registered entrypoints are:

- `ARC/identity.json`
- `ARC/dependencies.json`

## Ownership

`receiptos-base` owns ReceiptOS protocol, verification, replay, and receipt
implementation artifacts.

The AL intelligence repository is independently owned at `JSONWisdom/AL`.
Its implementation tree SHALL NOT be duplicated inside this repository.

## Extension directories

The following namespaces are reserved for repository-local ARC artifacts:

- `archive/`
- `criteria/`
- `examples/`
- `receipts/`
- `replay/`
- `schemas/`
- `tests/`

Empty namespaces are preserved with `.gitkeep` until substantive artifacts
are admitted.
