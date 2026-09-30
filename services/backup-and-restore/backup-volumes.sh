#!/usr/bin/env bash
set -euo pipefail

# Backs up docker volumes into timestamped tar.gz archives, one per volume.
#
#   ./backup-volumes.sh [output_dir] [name_pattern]
#
# output_dir    Directory to write archives into (default: backups/<timestamp>)
# name_pattern  grep -E pattern to filter volume names (default: all volumes)
cd "$(dirname "$0")"

OUT_DIR="${1:-backups/$(date +%Y%m%d-%H%M%S)}"
PATTERN="${2:-.}"

mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"

volumes="$(docker volume ls -q | grep -E "$PATTERN" || true)"

if [ -z "$volumes" ]; then
  echo "No volumes matched pattern '$PATTERN'"
  exit 0
fi

echo "Backing up to $OUT_DIR"
while IFS= read -r vol; do
  echo "Backing up volume: $vol"
  docker run --rm \
    -v "${vol}:/from:ro" \
    -v "${OUT_DIR}:/backup" \
    alpine tar czf "/backup/${vol}.tar.gz" -C /from .
done <<< "$volumes"

echo "Done. Archives written to $OUT_DIR"
