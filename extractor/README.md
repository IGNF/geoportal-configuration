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

## WMTS

**TODO**

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

Usage

```bash
python3 thumbnails.py
```

Ajoute les thumbnails dans le fichier JSON : `extractor/entreeCarto-test.json`