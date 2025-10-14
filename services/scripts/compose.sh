#!/usr/bin/env bash
set -euo pipefail

# Collect all compose files from the docker/ folder
compose_files=()
for file in docker/*.yml docker/*.yaml; do
  [ -e "$file" ] || continue
  compose_files+=("-f" "$file")
done

# Run docker compose with your .env file and all compose files
docker compose --env-file .env "${compose_files[@]}" "$@"

docker restart nginx || true
