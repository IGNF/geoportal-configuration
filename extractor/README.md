# [PROTOTYPE] Extraction des vignettes

> thumbnails

## WMS Vecteur / raster

> FIXME : limitation du nb de requetes !

Usage

```bash
python3 wms-v_thumbnail_extractor.py
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

> TODO : 
> - optimiser sur les niveaux du TMS (zoom)

> FIXME :
> - les zones de validité ne sont pas representatives des données

Usage

```bash
python3 wmts_thumbnail_extractor-v2.py
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

