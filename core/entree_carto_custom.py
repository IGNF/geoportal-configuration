import json

from core.config_merger import merge_edito
from core.requester import getEdito

def filter_specific_duplicates(input_dict):
    """
    Filtre un dictionnaire en supprimant les entrées où:
    - Le 'name' est dupliqué
    - ET l'entrée a 'serviceParams' contenant 'WMS'
    - ET l'autre entrée avec même 'name' a 'serviceParams' = 'WMTS'
    
    Args:
        input_dict (dict): Dictionnaire à filtrer
        
    Returns:
        dict: Dictionnaire filtré
    """
    # Dictionnaire pour tracker les names et leurs serviceParams
    name_tracker = {}
    
    # Premier passage: compiler les informations sur les doublons
    for key, entity in input_dict.items():
        if "name" in entity and "serviceParams" in entity:
            name = entity["name"]
            service_params = str(entity["serviceParams"])
            
            if name not in name_tracker:
                name_tracker[name] = {
                    'count': 1,
                    'wms_keys': [],
                    'wmts_keys': [],
                    'other_keys': []
                }
            else:
                name_tracker[name]['count'] += 1
                
            if "WMS" in service_params:
                name_tracker[name]['wms_keys'].append(key)
            elif "WMTS" in service_params:
                name_tracker[name]['wmts_keys'].append(key)
            else:
                name_tracker[name]['other_keys'].append(key)
    
    # Identifier les clés à supprimer
    keys_to_remove = set()
    
    for name, info in name_tracker.items():
        # S'il y a un doublon avec à la fois WMTS et WMS
        if info['count'] > 1 and info['wmts_keys'] and info['wms_keys']:
            # On garde le WMTS et on supprime le WMS
            keys_to_remove.update(info['wms_keys'])
    
    # Créer le dictionnaire résultat
    return {k: v for k, v in input_dict.items() if k not in keys_to_remove}

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
    # Ajoute la propriété key (utile pour l'entrée carto)
    for layerID, layerParams in edito_config["layers"].items():
        layerParams['key'] = layerID
    
    # Filtre les couches WMS qui dupliquent une couche WMTS
    edito_config["layers"] = filter_specific_duplicates(edito_config["layers"])

    with open("dist/entreeCarto.json", "w", encoding="utf-8") as file:
        file.writelines(json.dumps(edito_config, indent=2, ensure_ascii=False))