# [PROTOTYPE] Extraction des vignettes

> thumbnails

:information
> Une fois les vignettes générées, il faut faire un tri de celles que l'on souhaite garder !

## WMS Vecteur / raster

Usage

```bash
python3 wms-v_thumbnail_extractor.py > wms-v_thumbnail_extractor.log
```

```text
============================================================
WMS-v - 461 couches trouvées
============================================================
...
======================================================================
Résultats: 331 vignettes générées, 130 échecs
======================================================================
```

## WMTS / TMS

**FIXME** :

> * C'est plus simple de se baser sur les WMS pour extraire des vignettes !?
> * De plus, pour un TMS de données vecteur (type Mapbox), les tuiles brutes sont des données vectorielles (pbf, mvt, etc.) et n’ont pas de rendu image sans application d’un style (fichier de style Mapbox GL, etc.)...

Usage

```bash
python3 wmts_thumbnail_extractor.py > wmts_thumbnail_extractor.log
```

```text
  → 658 couches WMTS détectées

======================================================================
URL - https://data.geopf.fr/wmts
WMTS - 658 couches trouvées
Stratégie: Bbox couche (GetCapabilities) → Zones France prédéfinies
======================================================================
...
======================================================================
Résultats: ... vignettes générées, ... échecs
======================================================================
```

## entreeCarto

> Ajouter les thumbnails extraits dans le fichier JSON : `entreeCarto.json`

Usage

```bash
python3 thumbnails.py --input=entreeCarto.tmp --output=dist/entreeCarto.json
```
