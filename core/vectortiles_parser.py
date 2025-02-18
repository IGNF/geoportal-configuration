import json
import requests
import xmltodict

from core.key_resource_lister import keysServicesLayers
from core.generic_keys import GENERIC_KEYS

key_services_layers = keysServicesLayers()

def parseVectorTiles(tileMaps, key, referer):

    if key in GENERIC_KEYS() and key != "full" and "TMS" not in key_services_layers[key]:
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
    if not (key in GENERIC_KEYS()):
        serverUrl = "https://data.geopf.fr/private/tms/1.0.0/"

    for tileMap in tileMaps:
        layerName = tileMap["@href"].split("/")[-1]
        if key in GENERIC_KEYS() and key != "full" and layerName not in key_services_layers[key]["TMS"]:
            continue
        metadataURL = tileMap["@href"] + "/metadata.json"
        response = requests.get(metadataURL, headers={'Referer': referer})
        if response.status_code != 200:
            continue
        metadata = json.loads(response.text)

        styles = []
        response = requests.get(tileMap["@href"], headers={'Referer': referer})
        if response.status_code == 200:
            responseText = xmltodict.parse(response.text)["TileMap"]
            bbox = responseText["BoundingBox"]
            minTileSet = responseText["TileMap"]["TileSet"][0]
            maxTileSet = responseText["TileMap"]["TileSet"][-1]
            try:
                styles = filter(lambda metadata : metadata["@type"] == "Other" and metadata["@mime-type"] == "application/json", responseText["Metadata"])
                styles = list(styles)
            except KeyError:
                styles = []
        if len(styles) == 0 :
            continue

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
