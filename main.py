import json

from core.config_merger import merge_configs, merge_edito
from core.requester import getWMSRCapabilities, getWMSVCapabilities, getWMTSCapabilities, getWFSCapabilities, getTMSTileMaps, getEdito
from core.vectortiles_parser import parseVectorTiles
from core.wms_parser import parseWMS
from core.wmts_parser import parseWMTS
from core.wfs_parser import parseWFS
from core.key_resource_lister import createKeyServiceLayersFile

def main(keys, referer=""):
    createKeyServiceLayersFile()
    if not isinstance(keys, list):
        keys = [keys]
    keys = filter(lambda x: x != "", keys)
    list_configs = [
        config for key in keys
        for config in [
            parseWMTS(getWMTSCapabilities(key, referer), key),
            parseWMS(getWMSRCapabilities(key, referer), key),
            parseWMS(getWMSVCapabilities(key, referer), key),
            parseWFS(getWFSCapabilities(key, referer)[0], key, getWFSCapabilities(key, referer)[1]),
            parseVectorTiles(getTMSTileMaps(key, referer), key, referer)
        ]
    ]
    list_configs = [config for config in list_configs if isinstance(config, dict)]
    try:
        merged_config = merge_configs(list_configs)
    except IndexError:
        return "No key provided was valid"

    edito = getEdito()
    if edito:
        merged_config = merge_edito(merged_config, edito)
    
    # Filtre des couches selon les propriétés des layers
    conditions = {
        "defaultProjection": lambda prop: not any(substring in prop for substring in ["IGNF:LAMB93","EPSG:2154"]),
        "serviceParams": lambda prop: any(substring in prop["id"] for substring in ["WMTS", "WMS", "TMS"]),
    }
    merged_config["layers"] = {
        layerID: layerParams 
        for layerID, layerParams in merged_config["layers"].items()
        if all(
            prop in layerParams and condition(layerParams[prop])
            for prop, condition in conditions.items()
        )
    }


    return json.dumps(merged_config, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("keys", nargs="+")
    parser.add_argument("--referer", required=False, default="")
    keys = parser.parse_args().keys
    referer = parser.parse_args().referer

    config_name = keys[0]
    if len(keys) > 1:
        config_name = "custom"

    with open("dist/{}Config.json".format(config_name), "w", encoding="utf-8") as file:
        file.writelines(main(keys, referer))
