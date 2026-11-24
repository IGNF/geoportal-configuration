import json
from concurrent.futures import ThreadPoolExecutor

import xmltodict

from core.key_resource_lister import keysServicesLayers
from core.generic_keys import GENERIC_KEYS
from core import http_client

def _fetchTileMap(href, referer):
    """
    Télécharge metadata.json puis la description TileMap d'une couche TMS.
    Retourne (metadata_response, tilemap_response), ou None si metadata.json
    n'est pas disponible (la couche est alors ignorée, comme auparavant).
    """
    metadata_response = http_client.get(href + "/metadata.json", referer)
    if metadata_response.status_code != 200:
        return None
    return metadata_response, http_client.get(href, referer)


def parseVectorTiles(tileMaps, key, referer):
    key_services_layers = keysServicesLayers()
    generic_keys = GENERIC_KEYS()

    if key in generic_keys and key != "full" and "TMS" not in key_services_layers[key]:
        return False

    vector_tile_config = {
        "generalOptions": {
            "apiKeys": {
                key: []
            }
        },
        "layers" : {}
    }

    serverUrl = "https://data.geopf.fr/tms/1.0.0/"
    if not (key in generic_keys):
        serverUrl = "https://data.geopf.fr/private/tms/1.0.0/"

    selectedTileMaps = []
    for tileMap in tileMaps:
        layerName = tileMap["@href"].split("/")[-1]
        if key in generic_keys and key != "full" and layerName not in key_services_layers[key]["TMS"]:
            continue
        selectedTileMaps.append(tileMap)

    # Téléchargements en parallèle (2 requêtes par couche, ~850 couches pour
    # « full »). executor.map conserve l'ordre des couches : le fichier généré
    # est identique à la version séquentielle.
    with ThreadPoolExecutor(max_workers=http_client.get_max_workers()) as executor:
        responses = list(executor.map(
            lambda tileMap: _fetchTileMap(tileMap["@href"], referer),
            selectedTileMaps
        ))

    for tileMap, fetched in zip(selectedTileMaps, responses):
        if fetched is None:
            continue
        metadata_response, response = fetched
        layerName = tileMap["@href"].split("/")[-1]
        metadata = json.loads(metadata_response.text)

        metadatas = []
        styles = []
        if response.status_code == 200:
            responseText = xmltodict.parse(response.text)["TileMap"]
            bbox = responseText["BoundingBox"]
            minTileSet = responseText["TileSets"]["TileSet"][0]
            maxTileSet = responseText["TileSets"]["TileSet"][-1]
            try:
                if not isinstance(responseText["Metadata"], list):
                    responseText["Metadata"] = [responseText["Metadata"]]
                styles = filter(lambda metadata : metadata["@type"] == "Other" and metadata["@mime-type"] == "application/json", responseText["Metadata"])
                styles = list(styles)
                metadatas = list(responseText["Metadata"])
            except KeyError:
                styles = []
                metadatas = []
        if len(styles) == 0 :
            continue

        finalMetadatas = []
        for meta in metadatas:
            finalMetadatas.append({
                "name": meta["@href"].split("/")[-1].split(".")[0],
                "title": meta["@href"].split("/")[-1].split(".")[0],
                "url": meta["@href"]
                })
        
        finalStyles = []
        current = True
        for style in styles:
            finalStyles.append({
                "name": style["@href"].split("/")[-1].split(".")[0],
                "title": style["@href"].split("/")[-1].split(".")[0],
                "current": current,
                "url": style["@href"]
                })
            current = False


        vector_tile_config["generalOptions"]["apiKeys"][key].append(layerName + "$GEOPORTAIL:GPP:TMS")
        vector_tile_config["layers"][layerName + "$GEOPORTAIL:GPP:TMS"] = {
            "hidden": True,
            "queryable": False,
            "serviceParams": {
                "id": "GPP:TMS",
                "version": "1.0.0",
                "serverUrl": {
                    key: serverUrl
                }
            },
            "name": layerName,
            "title": layerName,
            "description": metadata["description"],
            "formats": [
                {
                    "current": True,
                    "name": "application/x-protobuf"
                }
            ],
            "metadata": finalMetadatas,
            "styles": finalStyles,
            "globalConstraint": {
                "crs": "EPSG:3857",
                "bbox": {
                    "left": float(bbox["@minx"]),
                    "right": float(bbox["@maxx"]),
                    "top": float(bbox["@maxy"]),
                    "bottom": float(bbox["@miny"]),
                },
                "minScaleDenominator": float(minTileSet["@units-per-pixel"]) / 0.00028,
                "maxScaleDenominator": float(maxTileSet["@units-per-pixel"]) / 0.00028
            },
            "defaultProjection": "EPSG:3857"
        }

    return vector_tile_config

if __name__ == "__main__":
    print(parseVectorTiles("essentiels"))
