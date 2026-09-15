#!/usr/bin/env bash
set -euo pipefail

# Run from services/. Reads ENABLE_* flags from .env and reconciles: stacks
# that are disabled get `down`'d, stacks that are enabled get the requested
# subcommand (default: `up -d`).
#
#   ./scripts/compose.sh              # up -d everything enabled, down everything disabled
#   ./scripts/compose.sh logs -f      # tail logs for everything enabled
#
# Pass -s to bypass the enable/disable file and target specific stacks directly
# (nothing gets torn down):
#   ./scripts/compose.sh -s nginx,sso logs -f
cd "$(dirname "$0")/.."

declare -A STACK_FILES=(
  [nginx]="nginx/docker-compose.nginx.yml"
  [sso]="sso/docker-compose.keycloak.yml"
  [control-plane]="tyk-stack/control-plane/docker-compose.control-plane.yml"
  [data-plane]="tyk-stack/data-plane/docker-compose.data-plane.yml"
  [oauth2]="tyk-stack/oauth2/docker-compose.oauth2.yml"
  [kong-control-plane]="kong/control-plane/docker-compose.kong.control-plane.yml"
  [kong-data-plane]="kong/data-plane/docker-compose.kong.data-plane.yml"
)
declare -A ENABLE_VARS=(
  [nginx]="ENABLE_NGINX"
  [sso]="ENABLE_SSO"
  [control-plane]="ENABLE_CONTROL_PLANE"
  [data-plane]="ENABLE_DATA_PLANE"
  [oauth2]="ENABLE_OAUTH2"
  [kong-control-plane]="ENABLE_KONG_CONTROL_PLANE"
  [kong-data-plane]="ENABLE_KONG_DATA_PLANE"
)

set -a
source .env
set +a

compose() {
  docker compose -p api-gateway-env --project-directory . --env-file .env "$@"
}

if [ "${1:-}" = "-s" ]; then
  stacks="$2"
  shift 2
  compose_files=("-f" "general/docker-compose.general.yml")
  IFS=',' read -ra names <<< "$stacks"
  for name in "${names[@]}"; do
    file="${STACK_FILES[$name]:-}"
    if [ -z "$file" ]; then
      echo "Unknown stack '$name'. Available: ${!STACK_FILES[*]}" >&2
      exit 1
    fi
    compose_files+=("-f" "$file")
  done
  [ "$#" -eq 0 ] && set -- up -d
  compose "${compose_files[@]}" "$@"
  exit 0
fi

up_files=("-f" "general/docker-compose.general.yml")
for name in "${!STACK_FILES[@]}"; do
  var="${ENABLE_VARS[$name]}"
  if [ "${!var:-false}" = "true" ]; then
    up_files+=("-f" "${STACK_FILES[$name]}")
  else
    # No --remove-orphans: this project spans multiple independently-toggled
    # compose files, and --remove-orphans would treat every OTHER currently
    # enabled stack's containers as orphans of *this* invocation and delete
    # them too. Down here only ever targets this one stack's own services.
    compose -f "general/docker-compose.general.yml" -f "${STACK_FILES[$name]}" down || true
  fi
done

[ "$#" -eq 0 ] && set -- up -d
compose "${up_files[@]}" "$@"

[ "${ENABLE_NGINX:-false}" = "true" ] && docker restart nginx || true
