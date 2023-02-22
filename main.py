from importlib.resources import contents
import json

from config_merger import merge_configs
from requester import getWMSRCapabilities, getWMSVCapabilities, getWMTSCapabilities
from wms_parser import parseWMS
from wmts_parser import parseWMTS

def main(key):
    list_configs = [
        parseWMTS(getWMTSCapabilities(key), key),
        parseWMS(getWMSRCapabilities(key), key),
        parseWMS(getWMSVCapabilities(key), key)
    ]
    list_configs = [config for config in list_configs if isinstance(config, dict)]
    merged_config = merge_configs(list_configs)

    return json.dumps(merged_config, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("key")
    key = parser.parse_args().key

    with open("dist/{}Config.json".format(key), "w", encoding="utf-8") as file:
        file.writelines(main(key))
