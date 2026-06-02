#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMPOSE_FILE="${PROJECT_DIR}/docker-compose.yml"
PROJECT_NAME="$(basename "$PROJECT_DIR" | tr '[:upper:]' '[:lower:]')"
DB_HOST_PORT="${DB_PORT:-5434}"
CLEAR_CACHE=false
DEEP_CACHE=false
COMPOSE_DOWN_ARGS=()

for arg in "$@"; do
  case "$arg" in
    --clear-cache|-c)
      CLEAR_CACHE=true
      ;;
    --deep-cache)
      CLEAR_CACHE=true
      DEEP_CACHE=true
      ;;
    *)
      COMPOSE_DOWN_ARGS+=("$arg")
      ;;
  esac
done

warn_port_conflict() {
  if ss -ltn "( sport = :${DB_HOST_PORT} )" 2>/dev/null | grep -q LISTEN; then
    echo "Aviso: el puerto ${DB_HOST_PORT} sigue ocupado en el host."
    echo "Esto suele indicar un proceso/contenedor ajeno a ${PROJECT_NAME}."
    echo "Puedes usar otro puerto al levantar:"
    echo "  DB_PORT=5435 docker compose up -d"
    echo "O identificar el proceso (requiere sudo):"
    echo "  sudo ss -ltnp '( sport = :${DB_HOST_PORT} )'"
  fi
}

cleanup_docker_cache() {
  [[ "$CLEAR_CACHE" == "true" ]] || return 0

  echo "Limpiando cache Docker para evitar estados residuales de jornadas anteriores..."
  docker container prune -f >/dev/null 2>&1 || true
  docker network prune -f >/dev/null 2>&1 || true
  docker image prune -f >/dev/null 2>&1 || true
  docker builder prune -f >/dev/null 2>&1 || true

  if [[ "$DEEP_CACHE" == "true" ]]; then
    echo "Modo profundo: limpiando volumenes no utilizados..."
    docker volume prune -f >/dev/null 2>&1 || true
  fi
}

cd "$PROJECT_DIR"

CONTAINER_IDS="$(docker ps -aq --filter "label=com.docker.compose.project=${PROJECT_NAME}" || true)"

if [[ -n "$CONTAINER_IDS" ]]; then
  while IFS= read -r container_id; do
    [[ -z "$container_id" ]] && continue
    docker exec -u root "$container_id" sh -lc 'kill -TERM 1 || kill -KILL 1 || true' || true
  done <<< "$CONTAINER_IDS"
fi

if docker compose -f "$COMPOSE_FILE" down --remove-orphans "${COMPOSE_DOWN_ARGS[@]}"; then
  cleanup_docker_cache
  warn_port_conflict
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

docker compose -f "$COMPOSE_FILE" down --remove-orphans "${COMPOSE_DOWN_ARGS[@]}"
cleanup_docker_cache
warn_port_conflict