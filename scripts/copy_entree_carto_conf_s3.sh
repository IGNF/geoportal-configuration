#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
rclone copy "$SCRIPT_DIR/../dist/entreeCarto.json" cartes_s3_dev:dev-ign-mut-cartes/entree-carto