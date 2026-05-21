# [PROTOTYPE] Generation du JSON de l'entré carto

Usage

```bash
python3 generator_entree_carto/entree_carto.py --input=dist/customConfig.json --output=entreeCarto_tmp.json 
```

On peut limiter les données à generer via le paramètre `count` :

```bash
python generator_entree_carto/entree_carto.py --input=dist/fullConfig.json --output=entreeCarto_tmp.json --count=100
```

## Déploiement sur S3
Dépôt du fihchier de configuration sur le s3 de IGN-MUT

Pour se faire :
- encoder la configuration rclone.conf à l'aide d'une passphrase
```bash
gpg --symmetric --cipher-algo AES256 rclone.conf
```
- créer une variable d'env secret sur github RCLONE_PASSPHRASE
- créer les variables d'env github S3_CONF_FILENAME (nom du fichier chiffré) et S3_PATH (bucket)
- pousser le fichier rclone.conf.gpg ou rclone.conf.qua.gpg