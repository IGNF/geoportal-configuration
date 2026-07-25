FROM python:3.10-slim

WORKDIR /app

# Outils système : gpg (déchiffrement rclone.conf) + rclone (upload S3)
RUN apt-get update && apt-get install -y --no-install-recommends \
      gnupg \
      curl \
      unzip \
    && RCLONE_VERSION="v1.68.2" \
    && curl -fsSL "https://github.com/rclone/rclone/releases/download/${RCLONE_VERSION}/rclone-${RCLONE_VERSION}-linux-amd64.zip" -o /tmp/rclone.zip \
    && unzip /tmp/rclone.zip -d /tmp/rclone \
    && mv /tmp/rclone/rclone-${RCLONE_VERSION}-linux-amd64/rclone /usr/local/bin/rclone \
    && chmod +x /usr/local/bin/rclone \
    && rm -rf /tmp/rclone /tmp/rclone.zip \
    && apt-get purge -y curl unzip \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python pour generator_entree_carto et extractor-thumbnails
COPY .docker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Scripts métier
COPY generator_entree_carto/ /app/generator_entree_carto/
COPY extractor-thumbnails/ /app/extractor-thumbnails/

# Scripts cron (à surcharger via la commande Docker)
COPY .docker/cron/ /app/cron/
RUN chmod +x /app/cron/*.sh

# Le contexte de build doit être la racine du projet :
#   docker build -f .docker/Dockerfile .
#
# Commande par défaut : génération de la configuration.
# Surchargeable au lancement du conteneur, par exemple :
#   docker run <image> /app/cron/cron_generate_thumbnails.sh
ENTRYPOINT ["/bin/bash"]
CMD ["/app/cron/cron_generate_configuration.sh"]
