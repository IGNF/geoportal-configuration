#!/usr/bin/env bash
# prod
# S3_PATH="cartes_s3_dev:dev-ign-mut-cartes/entree-carto"
# qua
# S3_PATH="cartes_s3_dev:qua-ign-mut-cartes/entree-carto"


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

rclone copy "$SCRIPT_DIR/../dist/entreeCarto.json" "$S3_PATH"