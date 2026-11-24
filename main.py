import json
from concurrent.futures import ThreadPoolExecutor

from core.config_merger import merge_configs
from core.requester import getWMSRCapabilities, getWMSVCapabilities, getWMTSCapabilities, getWFSCapabilities, getTMSTileMaps
from core.vectortiles_parser import parseVectorTiles
from core.wms_parser import parseWMS
from core.wmts_parser import parseWMTS
from core.wfs_parser import parseWFS
from core.key_resource_lister import createKeyServiceLayersFile
from core.http_client import get_max_workers

def main(keys, referer=""):
    createKeyServiceLayersFile()
    if not isinstance(keys, list):
        keys = [keys]
    non_null_keys = list(filter(lambda x: x != "", keys))
    list_configs = []
    for key in non_null_keys:
        # Les 5 GetCapabilities de la clé sont téléchargés en parallèle,
        # puis analysés séquentiellement dans le même ordre qu'auparavant.
        with ThreadPoolExecutor(max_workers=min(5, get_max_workers())) as executor:
            wmts = executor.submit(getWMTSCapabilities, key, referer)
            wms_r = executor.submit(getWMSRCapabilities, key, referer)
            wms_v = executor.submit(getWMSVCapabilities, key, referer)
            # Un seul appel WFS par clé (auparavant deux : un pour les
            # capabilities, un pour les namespaces).
            wfs = executor.submit(getWFSCapabilities, key, referer)
            tms = executor.submit(getTMSTileMaps, key, referer)
        wfs_capabilities, wfs_namespaces = wfs.result()
        list_configs += [
            parseWMTS(wmts.result(), key),
            parseWMS(wms_r.result(), key),
            parseWMS(wms_v.result(), key),
            parseWFS(wfs_capabilities, key, wfs_namespaces),
            parseVectorTiles(tms.result(), key, referer)
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
