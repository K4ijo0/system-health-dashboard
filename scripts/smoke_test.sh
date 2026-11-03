#!/usr/bin/env bash
set -euo pipefail

# The Jenkinsfile passes the deployed environment URL as the first argument.
# Removing a trailing slash keeps the endpoint URLs consistent.
BASE_URL="${1:?Usage: smoke_test.sh <base-url>}"
BASE_URL="${BASE_URL%/}"

# curl --fail makes a non-2xx response fail the script. Because of
# "set -e", the first failed check stops the script and fails the Jenkins stage.
echo "Checking ${BASE_URL}/health"
curl --fail --silent --show-error "${BASE_URL}/health" > /dev/null

# Confirm that the deployed application returns its version endpoint.
echo "Checking ${BASE_URL}/version"
curl --fail --silent --show-error "${BASE_URL}/version" > /dev/null

# Confirm that Prometheus can obtain application metrics from the deployment.
echo "Checking ${BASE_URL}/metrics"
curl --fail --silent --show-error "${BASE_URL}/metrics" > /dev/null

# Reaching this line means every smoke check returned a successful response.
echo "Smoke test passed for ${BASE_URL}"
