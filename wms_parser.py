def parseWMS(dict_capabilities, key):
    wms_config = {}

    if not isinstance(dict_capabilities["Layer"]["Layer"], list):
        dict_capabilities["Layer"]["Layer"] = [dict_capabilities["Layer"]["Layer"]]

    server_url = dict_capabilities["Request"]["GetMap"]["DCPType"]["HTTP"]["Get"]["OnlineResource"]["@xlink:href"]
    formats = _parseFormats(dict_capabilities)
    all_layers = _parseLayers(dict_capabilities["Layer"]["Layer"], key, server_url, formats)

    general_options = {}
    general_options["apiKeys"] = {}
    general_options["apiKeys"][key] = [layer_id for layer_id in all_layers.keys()]
    wms_config["generalOptions"] = general_options
    wms_config["layers"] = all_layers
    return wms_config

def _parseLayers(layers, key, server_url, formats):
    layers_config = {}
    for layer in layers:
        layer_id, layer_config = _parseLayer(layer, key, server_url, formats)
        layers_config[layer_id] = layer_config
    return layers_config

def _parseLayer(layer, key, server_url, formats):
    layer_id_suffix = "$GEOPORTAIL:OGC:WMS"
    if key == "inspire":
        layer_id_suffix = "$INSPIRE:OGC:WMS"

    layer_id = "{}{}".format(layer["Name"], layer_id_suffix)
    layer_config = {}
    layer_config["name"] = layer["Name"]
    layer_config["title"] = layer["Title"]
    layer_config["description"] = layer["Abstract"]

    global_constraint = {}
    global_constraint["maxScaleDenominator"] = float(layer["MaxScaleDenominator"])
    global_constraint["minScaleDenominator"] = float(layer["MinScaleDenominator"])
    global_constraint["bbox"] = {}
    global_constraint["bbox"]["left"] = float(layer["EX_GeographicBoundingBox"]["westBoundLongitude"])
    global_constraint["bbox"]["right"] = float(layer["EX_GeographicBoundingBox"]["eastBoundLongitude"])
    global_constraint["bbox"]["top"] = float(layer["EX_GeographicBoundingBox"]["northBoundLatitude"])
    global_constraint["bbox"]["bottom"] = float(layer["EX_GeographicBoundingBox"]["southBoundLatitude"])

    layer_config["globalConstraint"] = global_constraint

    service_params = {}
    service_params["id"] = "OGC:WMS"
    service_params["version"] = "1.3.0"
    service_params["serverUrl"] = {}
    service_params["serverUrl"][key] = server_url

    layer_config["serviceParams"] = service_params

    layer_config["defaultProjection"] = layer["BoundingBox"]["@CRS"]

    try:
        layer_config["queryable"] = bool(layer["@queryable"])
    except KeyError:
        layer_config["queryable"] = False

    layer_config["metadata"] = []
    if not isinstance(layer["MetadataURL"], list):
        layer["MetadataURL"] = [layer["MetadataURL"]]
    for metadata_url in layer["MetadataURL"]:
        metadata = {}
        metadata["format"] = metadata_url["Format"]
        metadata["url"] = metadata_url["OnlineResource"]["@xlink:href"]
        layer_config["metadata"].append(metadata)

    layer_config["styles"] = []
    layer_config["legends"] = []

    try:
        if not isinstance(layer["Style"], list):
            layer["Style"] = [layer["Style"]]
        for style in layer["Style"]:
            style_config = {}
            style_config["name"] = style["Name"]
            style_config["title"] = style["Title"]

            layer_config["styles"].append(style_config)

            legend_config = {}
            legend_config["format"] = style["LegendURL"]["Format"]
            legend_config["url"] = style["LegendURL"]["OnlineResource"]["@xlink:href"]

            layer_config["legends"].append(legend_config)

    except KeyError:
        pass

    layer_config["formats"] = formats

    return layer_id, layer_config

def _parseFormats(dict_capabilities):
    formats = []
    if not isinstance(dict_capabilities["Request"]["GetMap"]["Format"], list):
        dict_capabilities["Request"]["GetMap"]["Format"]
    test_first = True
    for format in dict_capabilities["Request"]["GetMap"]["Format"]:
        format_config = {}
        format_config["name"] = format
        format_config["current"] = test_first

        formats.append(format_config)
        if test_first:
            test_first = False

    return formats

if __name__ == "__main__":
    import json
    from requester import getWMSRCapabilities
    key = "essentiels"
    parsed_wms = parseWMS(getWMSRCapabilities(key), key)
    print(json.dumps(parsed_wms, indent=2, ensure_ascii=False))
