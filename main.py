import json

from core.config_merger import merge_configs
from core.requester import getWMSRCapabilities, getWMSVCapabilities, getWMTSCapabilities
from core.vectortiles_parser import parseVectorTiles
from core.wms_parser import parseWMS
from core.wmts_parser import parseWMTS

def main(keys, referer=""):
    if not isinstance(keys, list):
        keys = [keys]
    list_configs = [
        config for key in keys
        for config in [
            parseWMTS(getWMTSCapabilities(key, referer), key),
            parseWMS(getWMSRCapabilities(key, referer), key),
            parseWMS(getWMSVCapabilities(key, referer), key),
            parseVectorTiles(key)
        ]
    ]
    list_configs = [config for config in list_configs if isinstance(config, dict)]
    try:
        merged_config = merge_configs(list_configs)
    except IndexError:
        return "No key provided was valid"

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
