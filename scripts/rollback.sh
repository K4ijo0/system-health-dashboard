#!/usr/bin/env bash
set -euo pipefail

# Jenkins supplies the environment whose Compose service must be restored.
ENVIRONMENT="${1:?Usage: rollback.sh <staging|production>}"
IMAGE_NAME="${IMAGE_NAME:-system-health-dashboard}"

# Select the Compose project for the affected environment and reject typos
# before making any Docker changes.
case "${ENVIRONMENT}" in
  staging)
    COMPOSE_FILE="docker-compose.staging.yml"
    ;;
  production)
    COMPOSE_FILE="docker-compose.production.yml"
    ;;
  *)
    echo "Environment must be staging or production" >&2
    exit 2
    ;;
esac

PREVIOUS_IMAGE="${IMAGE_NAME}:${ENVIRONMENT}-previous"
CURRENT_IMAGE="${IMAGE_NAME}:${ENVIRONMENT}-current"

# A rollback is safe only when Jenkins has recorded a previous image tag.
if ! docker image inspect "${PREVIOUS_IMAGE}" >/dev/null 2>&1; then
  echo "Previous image ${PREVIOUS_IMAGE} was not found" >&2
  exit 1
fi

# Compose receives APP_IMAGE so it starts the previous release instead of
# rebuilding the current source tree. --force-recreate replaces the running
# container with one based on that previous image.
echo "Rolling ${ENVIRONMENT} back to ${PREVIOUS_IMAGE}"
APP_IMAGE="${PREVIOUS_IMAGE}" docker compose -f "${COMPOSE_FILE}" up -d --no-build --force-recreate
# Make the restored image the new current image for future deployments.
docker tag "${PREVIOUS_IMAGE}" "${CURRENT_IMAGE}"
echo "Rollback completed for ${ENVIRONMENT}"
