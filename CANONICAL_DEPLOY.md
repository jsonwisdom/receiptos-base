# Canonical Deploy Path

Use this path when the Vercel UI is showing stale projects, mirror projects, or old deployment commits.

## Goal

Deploy the canonical repository:

```text
jsonwisdom/receiptos-base
```

from branch:

```text
main
```

No mirror source should be treated as canonical.

## Step 1: GitHub canonical build receipt

A workflow named `Canonical Next Build` runs on every push to `main` and can also be started manually from GitHub Actions.

It performs:

```bash
npm install
npm run build
```

Use this as the first build receipt before trusting Vercel UI output.

## Step 2: Vercel CLI deploy from canonical checkout

From a local terminal or Cloud Shell:

```bash
git clone https://github.com/jsonwisdom/receiptos-base.git
cd receiptos-base
bash scripts/vercel-prod-deploy.sh
```

The script refuses to deploy unless the checked-out branch is `main`.

## Step 3: Capture external receipts

Set the deployed URL:

```bash
DEPLOY_URL="https://your-deployment.vercel.app"
```

Run:

```bash
curl -i "$DEPLOY_URL/api/frame"
curl -i "$DEPLOY_URL/api/health"
curl -i -X POST "$DEPLOY_URL/api/frame" \
  -H "Content-Type: application/json" \
  -d '{"untrustedData":{"inputText":"0x7ed8784f88dc16d9720dfd0a6d45a21b02f8d5d128eaf529ffeab0002e9c0af6"}}'
curl -i -X POST "$DEPLOY_URL/api/frame" \
  -H "Content-Type: application/json" \
  -d '{"untrustedData":{"inputText":"0xinvalid"}}'
curl -i -X POST "$DEPLOY_URL/api/frame" \
  -F "input=0x7ed8784f88dc16d9720dfd0a6d45a21b02f8d5d128eaf529ffeab0002e9c0af6"
curl -i "$DEPLOY_URL/og/witness-only.svg"
curl -i "$DEPLOY_URL/og/verified-blocked.svg"
```

## Doctrine

All API JSON must preserve:

```json
{
  "authority": false,
  "truth_claim": false,
  "status": "PENDING_SIGNATURE",
  "verdict": "WITNESS_ONLY"
}
```

No route may return `VERIFIED` until a later explicit signature-verification implementation exists.
