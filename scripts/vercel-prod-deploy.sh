#!/usr/bin/env bash
set -euo pipefail

EXPECTED_REPO="jsonwisdom/receiptos-base"
CURRENT_REPO="$(git config --get remote.origin.url || true)"
CURRENT_BRANCH="$(git branch --show-current || true)"
CURRENT_SHA="$(git rev-parse HEAD)"

printf 'ReceiptOS canonical Vercel deploy\n'
printf 'remote=%s\n' "$CURRENT_REPO"
printf 'branch=%s\n' "$CURRENT_BRANCH"
printf 'sha=%s\n' "$CURRENT_SHA"

if [[ "$CURRENT_BRANCH" != "main" ]]; then
  echo "Refusing deploy: checkout main first."
  exit 1
fi

if ! echo "$CURRENT_REPO" | grep -q "$EXPECTED_REPO"; then
  echo "Warning: remote does not visibly contain $EXPECTED_REPO"
  echo "Continue only if this is a verified canonical checkout."
fi

npm install
npm run build

if ! command -v vercel >/dev/null 2>&1; then
  echo "Installing Vercel CLI locally through npx path."
  npx vercel --version >/dev/null
  npx vercel --prod
else
  vercel --version
  vercel --prod
fi
