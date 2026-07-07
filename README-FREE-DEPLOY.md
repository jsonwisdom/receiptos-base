# Free-Tier Deploy Guide

This guide keeps Docket 57 on free infrastructure only.

## Constraints

- Vercel Hobby/free tier only
- No paid database
- No paid storage
- No paid queues
- No paid APIs
- No private keys
- No wallet secrets
- No environment variable that flips VERIFIED
- No runtime image generation
- No fake green

## Deploy Steps

1. Import `jsonwisdom/receiptos-base` into Vercel.
2. Choose the Hobby/free project tier.
3. Deploy from `main`.
4. If the deployment URL is not reflected in frame responses, set:

```text
NEXT_PUBLIC_URL=https://your-deployment.vercel.app
```

5. Redeploy.
6. Capture external curl receipts.

## Curl Receipts

Set your deployed URL:

```bash
DEPLOY_URL="https://your-deployment.vercel.app"
```

GET frame:

```bash
curl -X GET "$DEPLOY_URL/api/frame"
```

GET health:

```bash
curl -X GET "$DEPLOY_URL/api/health"
```

POST known EAS UID with JSON:

```bash
curl -X POST "$DEPLOY_URL/api/frame" \
  -H "Content-Type: application/json" \
  -d '{"untrustedData":{"inputText":"0x7ed8784f88dc16d9720dfd0a6d45a21b02f8d5d128eaf529ffeab0002e9c0af6"}}'
```

POST known EAS UID with form data:

```bash
curl -X POST "$DEPLOY_URL/api/frame" \
  -F "input=0x7ed8784f88dc16d9720dfd0a6d45a21b02f8d5d128eaf529ffeab0002e9c0af6"
```

POST invalid input:

```bash
curl -X POST "$DEPLOY_URL/api/frame" \
  -H "Content-Type: application/json" \
  -d '{"untrustedData":{"inputText":"0xinvalid"}}'
```

## Expected Responses

GET `/api/frame`:

- HTTP 200
- `status: PENDING_SIGNATURE`
- `verdict: WITNESS_ONLY`
- `authority: false`
- `truth_claim: false`

POST valid UID:

- HTTP 200
- known UID echoed in `uid`
- `invalid_input: false`
- `verdict: WITNESS_ONLY`

POST invalid UID:

- HTTP 200
- `invalid_input: true`
- `verdict: WITNESS_ONLY`

GET `/api/health`:

- HTTP 200
- `status: ok`
- `authority: false`
- `truth_claim: false`

## Deployment Checklist

- [ ] `npm run build` passes
- [ ] `GET /api/frame` returns 200
- [ ] `POST /api/frame` with known UID returns `WITNESS_ONLY`
- [ ] `POST /api/frame` with wrong input returns `invalid_input:true`
- [ ] `GET /api/health` returns `authority:false` and `truth_claim:false`
- [ ] No route returns `VERIFIED`
- [ ] Vercel Hobby/free deployment is active
- [ ] `NEXT_PUBLIC_URL` points at the deployment URL
- [ ] SVG assets serve from `/og/`
- [ ] External curl receipts are posted to Issue 57
