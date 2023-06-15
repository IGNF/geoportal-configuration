import json
from collections import defaultdict

def parseWMTS(dict_capabilities, key):
    if dict_capabilities == False:
        return False
    wmts_config = {}
    all_tms = _parseAllTMS(dict_capabilities["Contents"]["TileMatrixSet"])
    try:
        all_layers = _parseLayers(dict_capabilities["Contents"]["Layer"], all_tms, key)
    except KeyError:
        return False
    general_options = {}
    general_options["apiKeys"] = {}
    general_options["apiKeys"][key] = [layer_id for layer_id in all_layers.keys()]
    wmts_config["generalOptions"] = general_options

    wmts_config["layers"] = all_layers
    wmts_config["tileMatrixSets"] = all_tms

    return wmts_config

def _parseLayers(layers, all_tms, key):
    layers_config = {}
    for layer in layers:
        layer_id, layer_config = _parseLayer(layer, all_tms, key)
        layers_config[layer_id] = layer_config
    return layers_config

def _parseAllTMS(allTms):
    tile_matrix_sets = {}
    for tms in allTms:
        tms_id, tms_config = _parseTMS(tms)
        tile_matrix_sets[tms_id] = tms_config
    return tile_matrix_sets

def _parseLayer(layer, all_tms, key):
    layer_id = "{}$GEOPORTAIL:OGC:WMTS".format(layer["ows:Identifier"])
    layer_config = {}
    layer_config["name"] = layer["ows:Identifier"]
    layer_config["title"] = layer["ows:Title"]
    layer_config["description"] = layer["ows:Abstract"]

    global_constraint = {}
    scale_denominators = [
        tile_matrix["scaleDenominator"]
        for tile_matrix in
        all_tms[layer["TileMatrixSetLink"]["TileMatrixSet"]]["tileMatrices"].values()
    ]
    global_constraint["maxScaleDenominator"] = max(scale_denominators)
    global_constraint["minScaleDenominator"] = min(scale_denominators)
    global_constraint["bbox"] = {}
    global_constraint["bbox"]["left"] = float(layer["ows:WGS84BoundingBox"]["ows:LowerCorner"].split(" ")[0])
    global_constraint["bbox"]["right"] = float(layer["ows:WGS84BoundingBox"]["ows:UpperCorner"].split(" ")[0])
    global_constraint["bbox"]["top"] = float(layer["ows:WGS84BoundingBox"]["ows:UpperCorner"].split(" ")[1])
    global_constraint["bbox"]["bottom"] = float(layer["ows:WGS84BoundingBox"]["ows:LowerCorner"].split(" ")[1])

    layer_config["globalConstraint"] = global_constraint

    service_params = {}
    service_params["id"] = "OGC:WMTS"
    service_params["version"] = "1.0.0"
    service_params["serverUrl"] = {}
    service_params["serverUrl"][key] = "https://wmts.geopf.fr/rok4/wmts"

    layer_config["serviceParams"] = service_params

    layer_config["defaultProjection"] = all_tms[layer["TileMatrixSetLink"]["TileMatrixSet"]]["projection"]

    layer_config["wmtsOptions"] = {}
    layer_config["wmtsOptions"]["tileMatrixSetLink"] = layer["TileMatrixSetLink"]["TileMatrixSet"]
    layer_config["wmtsOptions"]["tileMatrixSetLimits"] = {}

    for tile_matrix in layer["TileMatrixSetLink"]["TileMatrixSetLimits"]["TileMatrixLimits"]:
        tile_matrix_set_limit = {}
        tile_matrix_set_limit["minTileRow"] = tile_matrix["MinTileRow"]
        tile_matrix_set_limit["maxTileRow"] = tile_matrix["MaxTileRow"]
        tile_matrix_set_limit["minTileCol"] = tile_matrix["MinTileCol"]
        tile_matrix_set_limit["maxTileCol"] = tile_matrix["MaxTileCol"]
        layer_config["wmtsOptions"]["tileMatrixSetLimits"][tile_matrix["TileMatrix"]] = tile_matrix_set_limit

    layer_config["styles"] = []
    layer_config["legends"] = []

    try:
        if not isinstance(layer["Style"], list):
            layer["Style"] = [layer["Style"]]
        for style in layer["Style"]:
            style_config = {}
            style_config["name"] = style["ows:Identifier"]
            style_config["title"] = style["ows:Title"]
            style_config["current"] = bool(style["@isDefault"])
            style_config["url"] = None

            layer_config["styles"].append(style_config)

            if not isinstance(style["LegendURL"], list):
                style["LegendURL"] = [style["LegendURL"]]
            for legend in style["LegendURL"]:
                legend_config = {}
                legend_config["format"] = legend["@format"]
                legend_config["url"] = legend["@xlink:href"]
                legend_config["minScaleDenominator"] = legend["@minScaleDenominator"]

                layer_config["legends"].append(legend_config)

    except KeyError:
        pass

    layer_config["formats"] = []
    if not isinstance(layer["Format"], list):
        layer["Format"] = [layer["Format"]]
    test_first = True
    for format in layer["Format"]:
        format_config = {}
        format_config["name"] = format
        format_config["current"] = test_first

        layer_config["formats"].append(format_config)
        if test_first:
            test_first = False

    return layer_id, layer_config

def _parseTMS(tms):
    tms_id = tms["ows:Identifier"]
    tms_config = {}
    tms_config["projection"] = tms["ows:SupportedCRS"]
    with open("nativeResolutions.json") as json_file:
        nativeResolutionsData = defaultdict(lambda: None, json.load(json_file))
    tms_config["nativeResolutions"] = nativeResolutionsData[tms_id]
    matrix_ids = []
    tile_matrices = {}
    for tile_matrix in tms["TileMatrix"]:
        tile_matrix_id, tile_matrix_config = _parseTileMatrix(tile_matrix)
        matrix_ids.append(tile_matrix_id)
        tile_matrices[tile_matrix_id] = tile_matrix_config
    tms_config["tileMatrices"] = tile_matrices

    return tms_id, tms_config

def _parseTileMatrix(tile_matrix):
    tile_matrix_id = tile_matrix["ows:Identifier"]
    tile_matrix_config = {}
    tile_matrix_config["matrixId"] = tile_matrix_id
    tile_matrix_config["matrixHeight"] = int(tile_matrix["MatrixHeight"])
    tile_matrix_config["matrixWidth"] = int(tile_matrix["MatrixWidth"])
    tile_matrix_config["scaleDenominator"] = float(tile_matrix["ScaleDenominator"])
    tile_matrix_config["tileHeight"] = int(tile_matrix["TileHeight"])
    tile_matrix_config["tileWidth"] = int(tile_matrix["TileWidth"])
    tile_matrix_config["topLeftCorner"] = {}
    tile_matrix_config["topLeftCorner"]["x"] = float(tile_matrix["TopLeftCorner"].split(" ")[0])
    tile_matrix_config["topLeftCorner"]["y"] = float(tile_matrix["TopLeftCorner"].split(" ")[1])
    return tile_matrix_id, tile_matrix_config

if __name__ == "__main__":
    import json
    from requester import getWMTSCapabilities
    key = "essentiels"
    parsed_wmts = parseWMTS(getWMTSCapabilities(key), key)
    print(json.dumps(parsed_wmts, indent=2, ensure_ascii=False))
