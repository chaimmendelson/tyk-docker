#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <src_volume> <dst_volume>"
  exit 1
fi

SRC="$1"
DST="$2"

# Ensure source volume exists
if ! docker volume inspect "$SRC" >/dev/null 2>&1; then
  echo "Source volume $SRC does not exist"
  exit 1
fi

# Create destination volume if it doesn’t exist
if ! docker volume inspect "$DST" >/dev/null 2>&1; then
  echo "Creating destination volume $DST"
  docker volume create "$DST"
fi

echo "Copying data from $SRC to $DST..."

# Use a temporary container to copy files
docker run --rm \
  -v "${SRC}:/from" \
  -v "${DST}:/to" \
  alpine sh -c "cd /from && cp -a . /to"

echo "Copy complete!"

# Remove the source volume
echo "Removing source volume $SRC..."
docker volume rm "$SRC"

echo "Done! Source volume $SRC deleted."