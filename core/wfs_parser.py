import xml.etree.ElementTree as ET


from core.key_resource_lister import keysServicesLayers
from core.generic_keys import GENERIC_KEYS

key_services_layers = keysServicesLayers()

def parseWFS(capabilities, key, namespaces):
    if capabilities == False:
        return False
    wfs_config = {}
    if key in GENERIC_KEYS() and key != "full" and "WFS" not in key_services_layers[key]:
        return False

    root = capabilities.getroot()
    server_url = ET.tostring(root.find('ows:OperationsMetadata', namespaces).find("ows:Operation", namespaces).find("ows:DCP", namespaces).find("ows:HTTP", namespaces).find("ows:Get", namespaces)).decode("utf-8")
    server_url = server_url.split("href=\"")[1].split("\"")[0]
    featureTypeList = root.find('FeatureTypeList', namespaces)
    all_layers = _parseLayers(featureTypeList, key, server_url, namespaces)

    general_options = {}
    general_options["apiKeys"] = {}
    general_options["apiKeys"][key] = [layer_id for layer_id in all_layers.keys()]
    wfs_config["generalOptions"] = general_options
    wfs_config["layers"] = all_layers
    return wfs_config

def _parseLayers(layers, key, server_url, namespaces):
    layers_config = {}
    for layer in layers.findall('FeatureType', namespaces):
        if layer == None:
            continue
        if key in GENERIC_KEYS() and key != "full" and layer.find("Name", namespaces).text not in key_services_layers[key]["WFS"]:
            continue
        layer_id, layer_config = _parseLayer(layer, key, server_url, namespaces)
        layers_config[layer_id] = layer_config
    return layers_config

def _parseLayer(layer, key, server_url, namespaces):
    layer_id_suffix = "$GEOPORTAIL:OGC:WFS"
    if key == "inspire":
        layer_id_suffix = "$INSPIRE:OGC:WFS"

    layer_id = "{}{}".format(layer.find("Name", namespaces).text, layer_id_suffix)
    layer_config = {}
    layer_config["name"] = layer.find("Name", namespaces).text
    layer_config["title"] = layer.find("Title", namespaces).text
    layer_config["description"] = layer.find("Abstract", namespaces).text

    global_constraint = {}
    global_constraint["minScaleDenominator"] = 0.
    global_constraint["maxScaleDenominator"] = 62236752975597

    global_constraint["bbox"] = {}
    bbox = layer.find("ows:WGS84BoundingBox", namespaces)
    global_constraint["bbox"]["left"] = float(bbox.find("ows:LowerCorner", namespaces).text.split(" ")[0])
    global_constraint["bbox"]["right"] = float(bbox.find("ows:UpperCorner", namespaces).text.split(" ")[0])
    global_constraint["bbox"]["top"] = float(bbox.find("ows:UpperCorner", namespaces).text.split(" ")[1])
    global_constraint["bbox"]["bottom"] = float(bbox.find("ows:LowerCorner", namespaces).text.split(" ")[1])

    layer_config["globalConstraint"] = global_constraint

    service_params = {}
    service_params["id"] = "OGC:WFS"
    service_params["version"] = "2.0.0"
    service_params["serverUrl"] = {}
    service_params["serverUrl"][key] = server_url

    layer_config["serviceParams"] = service_params

    layer_config["defaultProjection"] = ":".join(layer.find("DefaultCRS", namespaces).text.split("crs:")[1].split("::"))
    layer_config["queryable"] = False

    metadata = layer.find("MetadataURL", namespaces)
    if metadata:
        layer_config["metadata"] = [layer.find("MetadataURL", namespaces).get("xlink:href", namespaces)]
    else:
        layer_config["metadata"] = []
    layer_config["styles"] = []
    layer_config["legends"] = []

    layer_config["formats"] = []

    return layer_id, layer_config

if __name__ == "__main__":
    import json
    from requester import getWFSCapabilities
    key = "essentiels"
    parsed_wfs = parseWFS(getWFSCapabilities(key)[0], key, getWFSCapabilities(key)[1])
    print(json.dumps(parsed_wfs, indent=2, ensure_ascii=False))
