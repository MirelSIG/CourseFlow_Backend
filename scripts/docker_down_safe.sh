#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMPOSE_FILE="${PROJECT_DIR}/docker-compose.yml"
PROJECT_NAME="$(basename "$PROJECT_DIR" | tr '[:upper:]' '[:lower:]')"

cd "$PROJECT_DIR"

CONTAINER_IDS="$(docker ps -aq --filter "label=com.docker.compose.project=${PROJECT_NAME}" || true)"

if [[ -n "$CONTAINER_IDS" ]]; then
  while IFS= read -r container_id; do
    [[ -z "$container_id" ]] && continue
    docker exec -u root "$container_id" sh -lc 'kill -TERM 1 || kill -KILL 1 || true' || true
  done <<< "$CONTAINER_IDS"
fi

if docker compose -f "$COMPOSE_FILE" down --remove-orphans "$@"; then
  exit 0
fi

CONTAINER_IDS="$(docker ps -aq --filter "label=com.docker.compose.project=${PROJECT_NAME}" || true)"

if [[ -n "$CONTAINER_IDS" ]]; then
  echo "docker compose down failed; retrying cleanup after in-namespace stop..."
  while IFS= read -r container_id; do
    [[ -z "$container_id" ]] && continue
    docker exec -u root "$container_id" sh -lc 'kill -TERM 1 || kill -KILL 1 || true' || true
  done <<< "$CONTAINER_IDS"
fi

docker compose -f "$COMPOSE_FILE" down --remove-orphans "$@"