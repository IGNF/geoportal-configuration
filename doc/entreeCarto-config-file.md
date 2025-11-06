# 📘 Documentation – Workflow de génération du fichier `entreeCarto.json`

## 🎯 Objectif

Le fichier **`entreeCarto.json`** décrit les couches géographiques du Géoportail en combinant :

* des **informations techniques** issues des services OGC (WMS, WMTS, TMS),
* des **métadonnées** fournies par un service de recherche,
* des **ajouts éditoriaux** (producteurs, thématiques, propriétés spécifiques).

Ce document explique pas à pas comment ce fichier est généré.

---

## 🔗 Étapes principales du workflow

### 1. Récupération des sources de données

* **Services OGC** :

  * `getWMSRCapabilities`, `getWMTSCapabilities` → téléchargement des XML *GetCapabilities*.
  * `parseWMS`, `parseWMTS` → parsing en dictionnaires Python.
* **Service de recherche** : `searchMtdUrls()` fournit des informations complémentaires pour chaque couche :

  * `metadata_urls` (liens vers fiches ISO19139 ou JSON),
  * `theme` (thématique déclarée),
  * `producers` (organismes producteurs).
* **Fichier éditorial** : `getEdito()` surcharge ou enrichit certaines couches avec des champs supplémentaires (`producer`, `thematic`, etc.).

---

### 2. Fusion des configurations techniques

📌 **Script : config\_merger.py**

* `merge_configs(list_configs)` fusionne les résultats des services OGC :

  * rassemble les `apiKeys`,
  * regroupe les `layers`,
  * intègre les `tileMatrixSets`.
* Résultat : une configuration unique appelée `merged_config`.

---

### 3. Ajout et surcharge éditoriale

📌 **Script : config\_merger.py → merge\_edito**

* Si une couche est présente dans l’édito, ses propriétés sont surchargées.
* Sinon, des valeurs par défaut sont appliquées :

  * `"producer": ["Autres"]`,
  * `"thematic": ["Autres"]`,
  * `"base": False`.
* Les champs `producer` et `thematic` sont toujours transformés en **listes** pour homogénéité.

---

### 4. Enrichissement avec les métadonnées

📌 **Script : entree\_carto\_custom.py → generate\_entree\_carto\_conf**

* Pour chaque couche issue du service de recherche :

  * Ajout d’une vignette (`thumbnail`) si disponible (image png/jpeg ≤ 60×60 px, utilisation REQUEST HEAD).
  * Ajout des `metadata_urls`.
  * Ajout/mise à jour de la `thematic` (liste dérivée du champ `theme`).
  * Ajout/mise à jour du `producer` (depuis `producers`).

---

### 5. Nettoyage et normalisation

📌 **Script : entree\_carto\_custom.py**

* **Filtrage** : exclusion des couches qui n’ont pas de projection `IGNF:LAMB93` ou `EPSG:2154`, ou qui ne sont pas WMTS/WMS/TMS.
* **Suppression des doublons WMS/WMTS** : on conserve uniquement la couche WMTS.
* **Ajout d’une clé unique** : chaque couche reçoit `layerParams['key'] = layerID`.
* **Conversion des thématiques** via une table de correspondance (`getThematicConversionTable`).

---

### 6. Export final

* La configuration éditoriale et enrichie (`edito_config`) est sauvegardée dans :

  📂 `dist/entreeCarto.json`

---

## 📌 Origine des champs clés

* **`metadata`** :

  * issu directement des *GetCapabilities* (WMS, WMTS, TMS),
  * peut être un objet unique (url/type/format) ou **une liste d’objets**, par exemple :

    ```json
    "metadata": [
      {
        "format": "text/html",
        "url": "https://cartes.gouv.fr/catalogue/dataset/OCSGE.Boucle-Correction"
      },
      {
        "format": "application/xml",
        "url": "https://data.geopf.fr/csw?REQUEST=GetRecordById&SERVICE=CSW&VERSION=2.0.2&OUTPUTSCHEMA=http%3A%2F%2Fwww.isotc211.org%2F2005%2Fgmd&elementSetName=full&ID=OCSGE.Boucle-Correction"
      }
    ]
    ```
  * inclut des attributs comme le **type** (ex. `ISO19115:2003`, `other`) et le **format** (ex. `text/xml`, `text/html`, `application/json`),
  * reflète ce que le service OGC publie de manière déclarative.

* **`metadata_urls`** :

  * issus du service de recherche (`searchMtdUrls`),
  * liste de liens vers des fiches de métadonnées normalisées (ISO19139, parfois JSON),
  * peut contenir plusieurs entrées pour une même couche,
  * dans le cas particulier des couches TMS, **styles décrits en JSON**.

* **`producer`** :

  * service de recherche (`producers`),
  * ou fichier éditorial (`getEdito()`),
  * sinon par défaut `["Autres"]`.

* **`thematic`** :

  * service de recherche (`theme`),
  * fichier éditorial (`getEdito()`),
  * conversion via `getThematicConversionTable`,
  * sinon `["Autres"]`.

---

## 🔎 Différences entre `metadata` et `metadata_urls`

| Propriété          | Origine              | Contenu principal                                                                   | Usage                                              |
| ------------------ | -------------------- | ----------------------------------------------------------------------------------- | -------------------------------------------------- |
| **metadata**       | GetCapabilities      | URL (unique ou liste) + type (ex. ISO19115, `other`) + format (ex. XML, HTML, JSON) | Information déclarative fournie par le service OGC |
| **metadata\_urls** | Service de recherche | Liste d’URLs (ISO19139, JSON), styles TMS json                                      | Enrichissement éditorial et homogène               |

👉 En résumé :

* `metadata` = ce que le service OGC annonce de lui-même (parfois minimal, parfois une liste variée de formats HTML/XML/JSON).
* `metadata_urls` = informations éditoriales et riches fournies par le catalogue central.

### Cas particulier des TMS et styles JSON

* Les couches **TMS** n’exposent pas de balises `<Style>` dans leurs capabilities.
* Pour les couches TMS **IGN**, les styles sont disponibles directement via des URLs comme :

  * `https://data.geopf.fr/tms/1.0.0/PLAN.OSM`
  * `https://data.geopf.fr/tms/1.0.0/PLAN.IGN`
* Dans ces cas, les capabilities exposent un `metadata` avec `type=other` et `format=application/json`.
* Comme il n’existe pas de moyen certain de détecter un style, on applique la règle suivante :

  * **si la couche est TMS**, et que **`metadata.type=other`** avec une **URL se terminant en \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*`.json`**, alors on considère qu’il s’agit d’un style.
* Le service de recherche (`metadata_urls`) peut aussi référencer ces JSON de styles.

---

## 🗺️ Schéma simplifié du workflow

```
        ┌──────────────┐
        │ WMS/WMTS/TMS │
        │ Capabilities │
        └──────┬───────┘
               │
               ▼
      ┌───────────────────┐
      │ merge_configs()   │
      │ (config_merger.py)│
      └──────┬────────────┘
             │
   ┌─────────▼─────────┐
   │  merged_config     │
   └─────────┬─────────┘
             │
   ┌─────────▼─────────┐
   │  Enrichissement   │
   │  (searchMtdUrls + │
   │   getEdito + mtd) │
   └─────────┬─────────┘
             │
   ┌─────────▼─────────┐
   │ Nettoyage/filtrage │
   │ + conversion thèmes│
   └─────────┬─────────┘
             │
             ▼
   📄 dist/entreeCarto.json
```

---

## 📊 Exemple d’évolution d’une entrée `layer`

### Avant enrichissement (fusion brute des capabilities)

```json
"PLAN.IGN$GEOPORTAIL:OGC:TMS": {
  "name": "PLAN.IGN",
  "serviceParams": { "id": "TMS" },
  "defaultProjection": "EPSG:3857",
  "metadata": [
    {
      "url": "https://data.geopf.fr/tms/1.0.0/PLAN.IGN/styles.json",
      "type": "other",
      "format": "application/json"
    }
  ]
}
```

### Après enrichissement et surcharge éditoriale

```json
"PLAN.IGN$GEOPORTAIL:OGC:TMS": {
  "name": "PLAN.IGN",
  "serviceParams": { "id": "TMS" },
  "defaultProjection": "EPSG:3857",
  "key": "PLAN.IGN$GEOPORTAIL:OGC:TMS",
  "metadata": [
    {
      "url": "https://data.geopf.fr/tms/1.0.0/PLAN.IGN/styles.json",
      "type": "other",
      "format": "application/json"
    }
  ],
  "metadata_urls": [
    "https://www.geoportail.gouv.fr/csw?request=GetRecordById&id=67890"
  ],
  "styles": [
    { "id": "normal", "title": "Plan standard", "legend": "https://.../legend.png" },
    { "id": "light", "title": "Plan clair" }
  ],
  "producer": ["IGN"],
  "thematic": ["Cartographie de base"],
  "base": true,
  "thumbnail": "http://cartes.gouv.fr/annexes/url-vignette.png"
}
```

Cet exemple illustre :

* comment un TMS IGN peut exposer une ou plusieurs entrées `metadata` (dont certaines au format HTML ou XML, d’autres en JSON),
* comment ces JSON sont interprétés comme styles si les conditions sont réunies (`type=other`, `format=json`),
* et comment le service de recherche apporte un enrichissement supplémentaire via `metadata_urls`.

---

