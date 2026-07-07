# ROS-0006 Stream Metadata Patch

Docket: `jsonwisdom/receiptos-base#57`

## Commits

- `7c552a1a778eac18505f8a344f9c34424a39db01` — `/stream` now emits ROS-0006 Authorized Identity metadata.
- `14d77555f75703327919cce1ec64c15c27a5e450` — `/sign` now displays and signs the ROS-0006 Authorized Identity payload.

## Required `/stream` fields

```text
integrity_standard: ROS-0006
verification_method: erc1271
authorized_identity: 0xa380552a27b0a5a2874ea7aa52cac09f542002e8
authorized_identity_type: contract_account
chain_id: 8453
expected_magic: 0x1626ba7e
verdict: WITNESS_ONLY
authority: false
truth_claim: false
```

## Current deployment note

The latest tested deployment target was:

```text
https://receiptos-base.vercel.app
```

`/stream` responded successfully but reported:

```text
reason: erc1271_rpc_missing
status: PENDING_SIGNATURE
```

To complete live ERC-1271 verification, the Vercel project needs:

```text
BASE_RPC_URL=https://mainnet.base.org
```

Then redeploy.
