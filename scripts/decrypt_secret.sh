#!/bin/sh

if [ -z "${RCLONE_PASSPHRASE:-}" ]; then
  echo "Error: RCLONE_PASSPHRASE must be set and non-empty." >&2
  exit 1
fi

if [ -z "${S3_CONF_FILENAME:-}" ]; then
  echo "Error: S3_CONF_FILENAME must be set and non-empty." >&2
  exit 1
fi

if [ ! -f "$S3_CONF_FILENAME" ]; then
  echo "Error: encrypted rclone config file not found: $S3_CONF_FILENAME" >&2
  exit 1
fi

mkdir -p $HOME/.config/rclone
gpg --quiet --batch --yes --decrypt --passphrase="$RCLONE_PASSPHRASE" \
  --output "$HOME/.config/rclone/rclone.conf" "$S3_CONF_FILENAME"