import json
import sys

from core.config_merger import merge_configs
from core.requester import getWMSRCapabilities, getWMSVCapabilities, getWMTSCapabilities, getWFSCapabilities, getTMSTileMaps, CapabilitiesUnavailable
from core.vectortiles_parser import parseVectorTiles
from core.wms_parser import parseWMS
from core.wmts_parser import parseWMTS
from core.wfs_parser import parseWFS
from core.key_resource_lister import createKeyServiceLayersFile

def _wfsConfig(key, referer):
    # Un seul GetCapabilities : le document et ses namespaces doivent venir de la même réponse
    capabilities, namespaces = getWFSCapabilities(key, referer)
    return parseWFS(capabilities, key, namespaces)

def main(keys, referer=""):
    createKeyServiceLayersFile()
    if not isinstance(keys, list):
        keys = [keys]
    non_null_keys = list(filter(lambda x: x != "", keys))
    list_configs = [
        config for key in non_null_keys
        for config in [
            parseWMTS(getWMTSCapabilities(key, referer), key),
            parseWMS(getWMSRCapabilities(key, referer), key),
            parseWMS(getWMSVCapabilities(key, referer), key),
            _wfsConfig(key, referer),
            parseVectorTiles(getTMSTileMaps(key, referer), key, referer)
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

    # La config est calculée avant d'ouvrir le fichier : en cas d'échec, aucun
    # fichier (même vide) n'est écrit et la version publiée sur dist est conservée.
    try:
        content = main(keys, referer)
    except CapabilitiesUnavailable as error:
        print("ERROR: {} not generated: {}".format(config_name, error))
        sys.exit(1)

    with open("dist/{}Config.json".format(config_name), "w", encoding="utf-8") as file:
        file.writelines(content)
