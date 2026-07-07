# ROS-0002 — Automated Release Witness

ROS-0002 introduces a side-effect-free release witness workflow.

## Scope

This first witness layer proves:

```text
tag -> clean GitHub runner -> verifier -> PASS artifact upload
```

It does not pin IPFS, create EAS attestations, mint Zora assets, or create GitHub Releases.

## Current behavior

On supported release tags, the workflow:

1. Checks out full Git history.
2. Derives the ROS artifact ID from the tag.
3. Installs verifier dependencies.
4. Runs the existing ReceiptOS verifier against the checked-in evidence bundle.
5. Prints a replay receipt.
6. Uploads the evidence bundle and artifact as workflow artifacts.

## Supported tags

- `v1.0.0` -> `ROS-0001`
- `ros-0001` -> `ROS-0001`

Future ROS releases should extend the tag mapping and artifact path rules in small PRs.

## Non-goals for this PR

- No GitHub Secrets.
- No private keys.
- No IPFS pinning.
- No EAS writes.
- No Zora writes.
- No GitHub Release creation.

## Next layers

- ROS-0002.1 — IPFS pin witness
- ROS-0002.2 — EAS attestation witness
- ROS-0002.3 — GitHub Release creation
