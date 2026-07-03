# GitFix ERC-1271 CI Notes

The dual-path verifier imports `ethers`, so CI must install dependencies before running the identity-binding matrix.

Updated:

- `.github/workflows/identity-binding-matrix.yml`
  - commit `73f150c7c991db3ddb978d7a9cfd812497789ae7`
  - added `npm ci` before `node scripts/test-identity-binding-matrix.mjs`

- `cloudbuild-test-matrix.yaml`
  - commit `44aa7e20a22d3e9b7b179ebcfd1832be06dcd89d`
  - changed node step to bash and added `npm ci`

Boundary:

- CI verifies fail-closed behavior.
- ERC-1271 live verification still requires `BASE_RPC_URL` at runtime.
- No private keys or wallet secrets are required.
