#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:?Usage: rollback.sh <staging|production>}"
IMAGE_NAME="${IMAGE_NAME:-system-health-dashboard}"

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

if ! docker image inspect "${PREVIOUS_IMAGE}" >/dev/null 2>&1; then
  echo "Previous image ${PREVIOUS_IMAGE} was not found" >&2
  exit 1
fi

echo "Rolling ${ENVIRONMENT} back to ${PREVIOUS_IMAGE}"
APP_IMAGE="${PREVIOUS_IMAGE}" docker compose -f "${COMPOSE_FILE}" up -d --no-build --force-recreate
docker tag "${PREVIOUS_IMAGE}" "${CURRENT_IMAGE}"
echo "Rollback completed for ${ENVIRONMENT}"
