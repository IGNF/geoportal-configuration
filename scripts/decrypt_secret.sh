#!/bin/sh
mkdir -p $HOME/.config/rclone
gpg --quiet --batch --yes --decrypt --passphrase="$RCLONE_PASSPHRASE" \
  --output $HOME/.config/rclone/rclone.conf $S3_CONF_FILENAME