def merge_configs(list_configs):
    config1 = list_configs[0]
    list_configs.pop(0)

    full_api_keys = {}
    for api_key in config1["generalOptions"]["apiKeys"].keys():
        full_api_keys[api_key] = []

    for config in list_configs:
        for api_key in config["generalOptions"]["apiKeys"].keys():
            full_api_keys[api_key] = []

    for api_key, layers in config1["generalOptions"]["apiKeys"].items():
         full_api_keys[api_key].extend(layers)

    for config in list_configs:
        for api_key, layers in config["generalOptions"]["apiKeys"].items():
            full_api_keys[api_key].extend(layers)

    config1["generalOptions"]["apiKeys"] = full_api_keys
    for config2 in list_configs:
        config1["layers"].update(config2["layers"])

    for config2 in list_configs:
        try:
            config1["tileMatrixSets"] = config2["tileMatrixSets"]
        except KeyError:
            pass

    return config1