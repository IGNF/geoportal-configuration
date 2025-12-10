from core.thumbnail import get_image_dimensions, get_valid_thumbnail_from_mtd
import json 

def merge_service_de_recherche_infos(mtd_urls_layers, config, verbose=False):
    for item in mtd_urls_layers:
        if 'layer_name' in item:
            layerType = item["type"]
            layerName = item['layer_name']
            if layerType == "TMS":
                layerID = layerName + "$GEOPORTAIL:GPP:" + layerType
            else:
                layerID = layerName + "$GEOPORTAIL:OGC:" + layerType
            if layerID in config["layers"]:
                merge_layer_infos(config["layers"][layerID], item, verbose=verbose)
    return config
    
def merge_layer_infos(layer, merged_item, verbose=False):
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

    # INFO :
    # Recherche de la vignette dans les métadonnées
    # Si une vignette est disponible et valide dans le fichier edito.json, 
    # elle a priorité sur celle des métadonnées
    layerThumbnail = None
    for url in merged_item["metadata_urls"]:
        thumbnail = get_valid_thumbnail_from_mtd(url, 360, 360, verbose=verbose)
        if thumbnail is not None:
            layerThumbnail = thumbnail
            break  # On s'arrête dès qu'on trouve une vignette valide
    
    if layerThumbnail:
        props["thumbnail"] = layerThumbnail
    if 'thumbnail' in merged_item:
        image = get_image_dimensions(merged_item["thumbnail"])
        if image and image['width'] <= 360 and image['height'] <= 360:
            props["thumbnail"] = merged_item["thumbnail"]
    if 'theme' in merged_item:
        props["thematic"] = list(
            set(list(map(str.strip, merged_item["theme"].split(','))) + 
                list(map(str.strip, layer.get("thematic", []))))
        )
    if 'producers' in merged_item:
        props["producer"] = merged_item["producers"]
    if 'metadata_urls' in merged_item:
        props["metadata_urls"] = merged_item["metadata_urls"]
    layer.update(props)
    if verbose:
        print(f" --> layer : {layer['name']} : merged infos : {props} ")

def merge_layer_edito_infos(layer, merged_item, verbose=False):
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
        "thumbnail": "",
        "base": False,
        "title": ""
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
    elif "thematic" in layer:
        props["thematic"] = ensure_list(layer["thematic"])
        
    if 'producer' in merged_item:
        props["producer"] = list({
            v.strip() for v in ensure_list(merged_item["producer"]) if v and v.strip()
        })
    elif "producer" in layer:
        props["producer"] = ensure_list(layer["producer"])
    
    if 'thumbnail' in merged_item and merged_item['thumbnail']:
        props["thumbnail"] = merged_item["thumbnail"]
    elif "thumbnail" in layer:
        props["thumbnail"] = layer["thumbnail"]
        
    if 'base' in merged_item:
        props["base"] = merged_item["base"]
    elif 'base' in layer:
        props["base"] = layer["base"]
    
    if 'title' in merged_item and merged_item['title']:
        props["title"] = merged_item["title"]
    elif "title" in layer:
        props["title"] = layer["title"]
    
    layer.update(props)
    if verbose:
        print(f" --> layer : {layer['name']} : merged edito infos : {props} ")

def merge_edito(edito, config, verbose=False):
    for layerID, layer in edito["layers"].items():
        if layerID in config["layers"]:
            merge_layer_edito_infos(config["layers"][layerID], layer, verbose=verbose)
    del edito["layers"]
    config.update(edito)
    if verbose:
        with open('./edito_merged.json', "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    return config
