#!/usr/bin/env bash
set -euo pipefail

# Restores docker volumes from tar.gz archives produced by backup-volumes.sh.
# Creates any volume that doesn't already exist. Existing volume contents are
# wiped before the archive is extracted, so the volume ends up matching the
# backup exactly.
#
#   ./restore-volumes.sh <backup_dir> [name_pattern]
#
# backup_dir    Directory containing <volume>.tar.gz archives (required)
# name_pattern  grep -E pattern to filter which archives to restore (default: all)
cd "$(dirname "$0")"

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <backup_dir> [name_pattern]"
  exit 1
fi

BACKUP_DIR="$(cd "$1" && pwd)"
PATTERN="${2:-.}"

shopt -s nullglob
archives=("$BACKUP_DIR"/*.tar.gz)
shopt -u nullglob

if [ "${#archives[@]}" -eq 0 ]; then
  echo "No .tar.gz archives found in $BACKUP_DIR"
  exit 1
fi

for archive in "${archives[@]}"; do
  vol="$(basename "$archive" .tar.gz)"
  echo "$vol" | grep -qE "$PATTERN" || continue

  if ! docker volume inspect "$vol" >/dev/null 2>&1; then
    echo "Creating volume $vol"
    docker volume create "$vol" >/dev/null
  fi

  echo "Restoring volume: $vol"
  docker run --rm \
    -v "${vol}:/to" \
    -v "${BACKUP_DIR}:/backup:ro" \
    alpine sh -c "find /to -mindepth 1 -delete && tar xzf /backup/$(basename "$archive") -C /to"
done

echo "Done."
