import json

from config_merger import merge_configs
from requester import getWMSRCapabilities, getWMSVCapabilities, getWMTSCapabilities
from wms_parser import parseWMS
from wmts_parser import parseWMTS

def main(key):
    parsed_wms_r = parseWMS(getWMSRCapabilities(key), key)
    parsed_wms_v = parseWMS(getWMSVCapabilities(key), key)
    parsed_wmts = parseWMTS(getWMTSCapabilities(key), key)

    merged_config = merge_configs(parsed_wmts, parsed_wms_r)
    merged_config = merge_configs(merged_config, parsed_wms_v)

    return json.dumps(merged_config, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("key")
    key = parser.parse_args().key

    with open("dist/{}Config.json".format(key), "w") as file:
        file.writelines(main(key))
