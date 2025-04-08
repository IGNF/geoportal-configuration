import json

from core.config_merger import merge_edito
from core.requester import getEdito

def generate_entree_carto_conf(merged_config):
    edito = getEdito()
    if edito:
        edito_config = merge_edito(merged_config, edito)
    
    # Filtre des couches selon les propriétés des layers
    conditions = {
        "defaultProjection": lambda prop: not any(substring in prop for substring in ["IGNF:LAMB93","EPSG:2154"]),
        "serviceParams": lambda prop: any(substring in prop["id"] for substring in ["WMTS", "WMS", "TMS"]),
    }
    edito_config["layers"] = {
        layerID: layerParams 
        for layerID, layerParams in edito_config["layers"].items()
        if all(
            prop in layerParams and condition(layerParams[prop])
            for prop, condition in conditions.items()
        )
    }
    with open("dist/entreeCarto.json", "w", encoding="utf-8") as file:
        file.writelines(json.dumps(edito_config, indent=2, ensure_ascii=False))