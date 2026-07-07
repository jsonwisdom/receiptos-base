#!/usr/bin/env bash
set -euo pipefail

: "${BASE_RPC_URL:=https://mainnet.base.org}"
CONTRACT="0xd0c736467e0d496cc56209a36f28264b86c49582"

printf "%s\n" "$CONTRACT" > contract.txt

cast call "$CONTRACT" "contractURI()(string)" \
  --rpc-url "$BASE_RPC_URL" \
  > contractURI.txt

CID="$(cat contractURI.txt | sed 's#ipfs://##')"
printf "%s\n" "$CID" > metadata.cid

curl -L "https://w3s.link/ipfs/$CID" -o metadata.json

# Fail closed if gateway returns HTML or invalid JSON.
jq . metadata.json >/dev/null

jq -r '.image // .media // .animation_url // .content.uri // empty' metadata.json > media.uri

MEDIA_URI="$(cat media.uri)"
MEDIA_CID="${MEDIA_URI#ipfs://}"
printf "%s\n" "$MEDIA_CID" > media.cid

mkdir -p media
curl -L "https://w3s.link/ipfs/$MEDIA_CID" -o media/artifact

sha256sum \
  metadata.json \
  media/artifact \
  contract.txt \
  contractURI.txt \
  metadata.cid \
  media.cid \
  media.uri \
  > sha256sums.txt

sha256sum -c sha256sums.txt

echo
echo "---- PASTE THIS BLOCK BACK ----"
echo "contractURI=$(cat contractURI.txt)"
echo "metadataCID=$(cat metadata.cid)"
echo "mediaCID=$(cat media.cid)"
echo "sha256Metadata=$(sha256sum metadata.json | awk '{print $1}')"
echo "sha256Media=$(sha256sum media/artifact | awk '{print $1}')"
echo "name=$(jq -r '.name // empty' metadata.json)"
echo "ticker=$(jq -r '.ticker // .symbol // empty' metadata.json)"
echo "description=$(jq -r '.description // empty' metadata.json)"
