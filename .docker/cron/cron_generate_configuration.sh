#!/bin/bash
set -euo pipefail

WORKDIR="/app"

# ---------------------------------------------------------------------------
# Variables d'environnement requises 
# ---------------------------------------------------------------------------

# - CONFIG_INPUT      : chemin vers le fichier de configuration d'entrée (ex. fullConfig.json)
# - RCLONE_PASSPHRASE : passphrase pour déchiffrer le fichier de configuration rclone
# - RCLONE_GPG_FILE   : nom du fichier chiffré contenant la configuration rclone


# ---------------------------------------------------------------------------
# Variables d'environnement optionnelles 
# ---------------------------------------------------------------------------

# - S3_GATEWAY_PATH : url du gateway S3 (optionnel)
#     par défaut, https://cartes.gouv.fr/files/entree-carto/

S3_GATEWAY_PATH="${S3_GATEWAY_PATH:-https://cartes.gouv.fr/files/entree-carto/}"

# - S3_PATH : chemin relatif dans le bucket S3 où uploader un fichier (optionnel)
#     prod (par défaut):
#     S3_PATH="cartes_s3_dev:prd-ign-mut-cartes/entree-carto"
#     dev:
#     S3_PATH="cartes_s3_dev:dev-ign-mut-cartes/entree-carto"
#     qua:
#     S3_PATH="cartes_s3_dev:qua-ign-mut-cartes/entree-carto"

S3_PATH="${S3_PATH:-cartes_s3_dev:prd-ign-mut-cartes/entree-carto}"

# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------

ENTREE_CARTO_OUTPUT="/app/entreeCarto.json"
ENTREE_CARTO_OUTPUT_TEMP="/app/entreeCarto.json.tmp"

echo "[$(date -Iseconds)] Starting generation of the entreeCarto configuration..."

cd "$WORKDIR"

# ---------------------------------------------------------------------------
# Génération du fichier entreeCarto
# ---------------------------------------------------------------------------

python3 generator_entree_carto/entree_carto.py \
  --input="${CONFIG_INPUT:-}" \
  --output="$ENTREE_CARTO_OUTPUT_TEMP"

echo "[$(date -Iseconds)] Generation completed: $ENTREE_CARTO_OUTPUT_TEMP"

# ---------------------------------------------------------------------------
# Recherche des miniatures et mise à jour du fichier entreeCarto
# ---------------------------------------------------------------------------

python3 extractor-thumbnails/thumbnails.py \
  --input="$ENTREE_CARTO_OUTPUT_TEMP" \
  --output="$ENTREE_CARTO_OUTPUT" \
  --base-url="$S3_GATEWAY_PATH"

echo "[$(date -Iseconds)] Generation completed: $ENTREE_CARTO_OUTPUT"

# ---------------------------------------------------------------------------
# Upload S3 (optionnel — déclenché si RCLONE_GPG_FILE ou RCLONE_PASSPHRASE est défini)
# ---------------------------------------------------------------------------

if [ -n "${RCLONE_GPG_FILE:-}" ] && [ -n "${RCLONE_PASSPHRASE:-}" ]; then
  echo "[$(date -Iseconds)] Déchiffrement de la configuration rclone..."

  if [ ! -f "$RCLONE_GPG_FILE" ]; then
    echo "Error: rclone configuration file not found: $RCLONE_GPG_FILE" >&2
    exit 1
  fi

  mkdir -p "$HOME/.config/rclone"
  gpg --quiet --batch --yes --decrypt \
    --passphrase="$RCLONE_PASSPHRASE" \
    --output "$HOME/.config/rclone/rclone.conf" "$RCLONE_GPG_FILE"

  MIN_OUTPUT="${ENTREE_CARTO_OUTPUT%.json}.min.json"
  echo "[$(date -Iseconds)] Upload vers S3 : $S3_PATH/entreeCarto.json"
  rclone copyto "$MIN_OUTPUT" "$S3_PATH/entreeCarto.json"
  echo "[$(date -Iseconds)] Upload completed."
fi

echo "[$(date -Iseconds)] Script completed successfully."