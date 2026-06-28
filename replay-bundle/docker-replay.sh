#!/usr/bin/env bash
set -euo pipefail

IMAGE="receiptos-replay:round-022"
EXPECTED_HASH="0xdf0e9e385ad3f3ad610f3e4cae6506ab2c83fa5beb75dd921402070c4a80603f"

cd "$(dirname "$0")"

docker build --no-cache -t "$IMAGE" .

docker run --rm "$IMAGE" | tee docker-replay.log

ACTUAL_HASH="$(grep 'Receipt hash:' docker-replay.log | tail -1 | awk '{print $3}')"

if [ "$ACTUAL_HASH" = "$EXPECTED_HASH" ]; then
  echo "ROUND_022 DOCKER REPLAY: PASS"
else
  echo "ROUND_022 DOCKER REPLAY: FAIL"
  exit 1
fi

docker image inspect "$IMAGE" --format='{{.Id}}' > docker-image-id.txt
sha256sum Dockerfile docker-replay.sh docker-replay.log docker-image-id.txt > round-022-docker-sha256.txt
