# Cron Jobs

## Docker

> Execution local avec les commandes docker

```bash
# Build depuis la racine du projet
docker build -f .docker/Dockerfile -t geoportal-configuration-cron .

# Génération de la configuration sans upload S3 (optionnel)
docker run --rm 
  -v "$(pwd)/customConfig.json:/app/customConfig.json:ro"
  -e CONFIG_INPUT=/app/customConfig.json
  geoportal-configuration-cron

# Génération de la configuration avec upload S3
docker run --rm 
  -v "$(pwd)/customConfig.json:/app/customConfig.json:ro"
  -v "$(pwd)/rclone.conf.gpg:/app/rclone.conf.gpg:ro"
  -e CONFIG_INPUT=/app/customConfig.json
  -e RCLONE_GPG_FILE=/app/rclone.conf.gpg
  -e RCLONE_PASSPHRASE='ta_passphrase'
  -e S3_PATH='cartes_s3_dev:prd-ign-mut-cartes/entree-carto'
  -e S3_GATEWAY_PATH='https://cartes.gouv.fr/files/entree-carto/'
  geoportal-configuration-cron

# Génération de la configuration avec un fichier .env
CONFIG_INPUT=/app/customConfig.json
RCLONE_GPG_FILE=/app/rclone.conf.gpg
RCLONE_PASSPHRASE=ta_passphrase
S3_PATH=cartes_s3_dev:prd-ign-mut-cartes/entree-carto
S3_GATEWAY_PATH=https://cartes.gouv.fr/files/entree-carto/

docker run --rm
  --env-file .env
  -v "$(pwd)/customConfig.json:/app/customConfig.json:ro"
  -v "$(pwd)/rclone.conf.gpg:/app/rclone.conf.gpg:ro"
  geoportal-configuration-cron

# TODO : Possibilité de surcharger la CMD avec d'autre shell
docker run geoportal-configuration-cron /app/cron/cron_generate_thumbnails.sh
```

## Docker Compose

> Execution locale avec docker-compose

```bash
# Depuis la racine du projet

# 1) Génération locale (sans upload S3)
docker compose -f .docker/docker-compose.yml run --rm generate-configuration

# 2) Génération avec upload S3
docker compose -f .docker/docker-compose.yml --profile s3 run --rm generate-configuration-s3

# 3) Génération avec upload S3 et surcharge via un .env
docker compose \
  --env-file .docker/.env.s3.example \
  -f .docker/docker-compose.yml \
  --profile s3 run --rm generate-configuration-s3
```

Notes:

- Le service `generate-configuration-s3` monte `rclone.conf.gpg` depuis la racine du projet vers `/app/rclone.conf.gpg`.
- Les fichiers générés sont écrits dans la racine: `entreeCarto.json` et `entreeCarto.min.json`.

## Workflow (docker)

Actuellement, il y'a quelques limites au process local.

L'execution de la génération du fichier de configuration :

- il utilise un fichier de configuration (ex. fullConfug.json) en variable d'environnement
- il faut donc le télécharger au préalable
- et, le placer à la racine du projet

La recherche des miniatures (mise à jour):

- il faut generer les miniatures
- puis, supprimer les miniatures non acceptables
- reconstruire l'image docker
- et, copier les miniatures sur le S3 via un script

**Todo :**
> Ajouter un script / shell pour copier les miniatures sur le S3

## Job sur l'environnement cartes.gouv.fr

> **TODO**
