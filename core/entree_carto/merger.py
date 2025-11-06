from core.entree_carto.thumbnail import get_valid_thumbnail_from_mtd
import json 

def merge_service_de_recherche_infos(mtd_urls_layers, config):
    for item in mtd_urls_layers:
        if 'layer_name' in item:
            layerType = item["type"]
            layerName = item['layer_name']
            if layerType == "TMS":
                layerID = layerName + "$GEOPORTAIL:GPP:" + layerType
            else:
                layerID = layerName + "$GEOPORTAIL:OGC:" + layerType
            if layerID in config["layers"]:
                merge_layer_infos(config["layers"][layerID], item)
    return config
    
def merge_layer_infos(layer, merged_item):
    """
    Fusionne les métadonnées d'un élément merged_item dans le dictionnaire layer.
    Args:
        layer (dict): Dictionnaire à mettre à jour
        merged_item (dict): Dictionnaire avec les métadonnées à fusionner
    Returns:
        None: Le dictionnaire layer est mis à jour en place
    """
    props = {
        "thumbnail": "",
        "producer": "",
        "thematic": [],
        "metadata_urls": []
    }

    layerThumbnail = next((u for u in (get_valid_thumbnail_from_mtd(url, 360, 360) for url in merged_item["metadata_urls"]) if u), None)
    if layerThumbnail:
        props["thumbnail"] = layerThumbnail
    if 'theme' in merged_item:
        props["thematic"] = list(
            set(list(map(str.strip, merged_item["theme"].split(','))) + 
                list(map(str.strip, layer.get("thematic", []))))
        )
    if 'producer' in merged_item:
        props["producer"] = merged_item["producer"]
    if 'metadata_urls' in merged_item:
        props["metadata_urls"] = merged_item["metadata_urls"]
    layer.update({k: v for k, v in props.items()})

def merge_layer_edito_infos(layer, merged_item):
    """
    Fusionne les métadonnées d'un élément merged_item dans le dictionnaire layer.
    Args:
        layer (dict): Dictionnaire à mettre à jour
        merged_item (dict): Dictionnaire avec les métadonnées à fusionner
    Returns:
        None: Le dictionnaire layer est mis à jour en place
    """
    props = {
        "producer": [],
        "thematic": [],
        "base": False
    }
    def ensure_list(value):
        if value is None:
            return []
        if isinstance(value, str):
            return list(map(str.strip, value.split(',')))
        if isinstance(value, list):
            return list(map(str.strip, value))
        return []

    if 'thematic' in merged_item:
        props["thematic"] = list({
            v.strip() for v in ensure_list(merged_item["thematic"]) if v and v.strip()
        })
    if 'producer' in merged_item:
        props["producer"] = list({
            v.strip() for v in ensure_list(merged_item["producer"]) if v and v.strip()
        })
    if 'base' in merged_item:
        props["base"] = merged_item["base"]
    layer.update({k: v for k, v in props.items()})


def merge_edito(edito, config):
    for layerID, layer in edito["layers"].items():
        if layerID in config["layers"]:
            merge_layer_edito_infos(config["layers"][layerID], layer)
    del edito["layers"]
    config.update(edito)
    with open('./edito_merged.json', "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    return config

if __name__ == "__main__":
    import json
    from requester import getWMSRCapabilities, getWMTSCapabilities
    from wms_parser import parseWMS
    from wmts_parser import parseWMTS
    key = "essentiels"
    parsed_wms = parseWMS(getWMSRCapabilities(key), key)
    parsed_wmts = parseWMTS(getWMTSCapabilities(key), key)

    print(json.dumps(merge_configs(parsed_wms, parsed_wmts), indent=2, ensure_ascii=False))