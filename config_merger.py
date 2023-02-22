def merge_configs(list_configs):
    config1 = list_configs[0]
    list_configs.pop(0)
    for apiKey1, layers1 in config1["generalOptions"]["apiKeys"].items():
        for config2 in list_configs:
            for apiKey2, layers2 in config2["generalOptions"]["apiKeys"].items():
                if apiKey1 == apiKey2:
                    layers1.extend(layers2)

    for config2 in list_configs:
        config1["layers"].update(config2["layers"])

    for config2 in list_configs:
        try:
            config1["tileMatrixSets"] = config2["tileMatrixSets"]
        except KeyError:
            pass

    return config1

if __name__ == "__main__":
    import json
    from requester import getWMSRCapabilities, getWMTSCapabilities
    from wms_parser import parseWMS
    from wmts_parser import parseWMTS
    key = "essentiels"
    parsed_wms = parseWMS(getWMSRCapabilities(key), key)
    parsed_wmts = parseWMTS(getWMTSCapabilities(key), key)

    print(json.dumps(merge_configs(parsed_wms, parsed_wmts), indent=2, ensure_ascii=False))