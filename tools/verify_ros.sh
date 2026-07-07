#!/usr/bin/env bash
set -euo pipefail

ROS_DIR="${1:?Usage: ./tools/verify_ros.sh evidence/ROS-XXXX}"
BUNDLE="$ROS_DIR/evidence-bundle.json"

test -f "$BUNDLE"

ROS_ID="$(jq -r .rosId "$BUNDLE")"
AUTHORITY="$(jq -r '.eas.authority // .authority' "$BUNDLE")"
DIGEST="$(jq -r .artifactDigest "$BUNDLE" | sed 's/^sha256://')"
CID="$(jq -r .ipfsCid "$BUNDLE")"
EAS_UID="$(jq -r '.eas.easAttestationUid // ""' "$BUNDLE")"
TX_HASH="$(jq -r '.eas.transactionHash // ""' "$BUNDLE")"

test "$AUTHORITY" = "false"
test -n "$DIGEST"
test -n "$CID"
test -n "$EAS_UID"
test -n "$TX_HASH"

ARCHIVE="evidence/${ROS_ID%-v1}.tar"
[ ! -f "$ARCHIVE" ] && ARCHIVE="evidence/ROS-0004-runtime-config-core.tar"

echo "$DIGEST  $ARCHIVE" | sha256sum -c -
ipfs cat "$CID" >/dev/null

echo "PASS: $ROS_ID"
echo "ARCHIVE: $ARCHIVE"
echo "CID: $CID"
echo "EAS UID: $EAS_UID"
echo "TX: $TX_HASH"
