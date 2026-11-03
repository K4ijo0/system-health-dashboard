#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:?Usage: smoke_test.sh <base-url>}"
BASE_URL="${BASE_URL%/}"

echo "Checking ${BASE_URL}/health"
curl --fail --silent --show-error "${BASE_URL}/health" > /dev/null

echo "Checking ${BASE_URL}/version"
curl --fail --silent --show-error "${BASE_URL}/version" > /dev/null

echo "Checking ${BASE_URL}/metrics"
curl --fail --silent --show-error "${BASE_URL}/metrics" > /dev/null

echo "Smoke test passed for ${BASE_URL}"
