#!/usr/bin/env bash
# prod
# S3_PATH="cartes_s3_dev:dev-ign-mut-cartes/entree-carto"
# qua
# S3_PATH="cartes_s3_dev:qua-ign-mut-cartes/entree-carto"


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "${S3_PATH:-}" ]; then
  echo "Error: S3_PATH must be set and non-empty." >&2
  exit 1
fi

# On uploade la version minifiée sous le nom entreeCarto.json sur S3.
rclone copyto "$SCRIPT_DIR/../dist/entreeCarto.min.json" "$S3_PATH/entreeCarto.json"