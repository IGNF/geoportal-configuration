def filter_layers(layers_dict, verbose=False):
    """
    Filtre les couches dans un dictionnaire en fonction de conditions données.
    
    Args:
        layers_dict (dict): Dictionnaire des couches à filtrer
    
    Returns:
        dict: Dictionnaire des couches filtrées
    """
    # Filtre des couches selon les propriétés des layers
    conditions = {
        "defaultProjection": lambda prop: not any(substring in prop for substring in ["IGNF:LAMB93","EPSG:2154"]),
        "serviceParams": lambda prop: any(substring in prop["id"] for substring in ["WMTS", "WMS", "TMS"]),
    }
    filtered_layers =  {
        layerID: layerParams 
        for layerID, layerParams in layers_dict.items()
        if all(
            prop in layerParams and condition(layerParams[prop])
            for prop, condition in conditions.items()
        )
    }
    return filtered_layers

def filter_specific_duplicates(input_dict, verbose=False):
    """
    Filtre un dictionnaire en supprimant les entrées où:
    - Le 'name' est dupliqué  (y compris les noms formatés avec _wms/_wmts)
    - ET l'entrée a 'serviceParams' contenant 'WMS'
    - ET l'autre entrée avec même 'name' a 'serviceParams' = 'WMTS'
    
    Args:
        input_dict (dict): Dictionnaire à filtrer
        
    Returns:
        dict: Dictionnaire filtré
    """
    # Dictionnaire pour tracker les names et leurs serviceParams
    base_name_tracker = {}
    
    # Premier passage: compiler les informations sur les doublons
    for key, entity in input_dict.items():
        if "name" in entity and "serviceParams" in entity:
            name = entity["name"]
            service_params = str(entity["serviceParams"])
            
            # Extraire le nom de base (sans _wms, _wmts, _wmsr)
            suffixes = ["_wms", "_wmts", "_wmsr"]
            for suffix in suffixes:
                if name.endswith(suffix):
                    base_name = name[:-len(suffix)]
                    break
                else:
                    base_name = name

            if base_name not in base_name_tracker:
                base_name_tracker[base_name] = {
                    'count': 1,
                    'wms_keys': [],
                    'wmts_keys': [],
                    'other_keys': []
                }
            else:
                base_name_tracker[base_name]['count'] += 1
                
            if "WMS" in service_params:
                base_name_tracker[base_name]['wms_keys'].append(key)
            elif "WMTS" in service_params:
                base_name_tracker[base_name]['wmts_keys'].append(key)
            else:
                base_name_tracker[base_name]['other_keys'].append(key)
    
    # Identifier les clés à supprimer
    keys_to_remove = set()
    
    for base_name, info in base_name_tracker.items():
        # S'il y a un doublon avec à la fois WMTS et WMS
        if info['count'] > 1 and info['wmts_keys'] and info['wms_keys']:
            # On garde le WMTS et on supprime le WMS
            keys_to_remove.update(info['wms_keys'])
    
    # Créer le dictionnaire résultat
    return {k: v for k, v in input_dict.items() if k not in keys_to_remove}

def add_layers_default_values(layers, verbose=False):
    """
    Ajoute des valeurs par défaut pour certaines clés manquantes dans les couches.
    Args:
        layers (dict): Dictionnaire des couches à traiter
    Returns:
        dict: Dictionnaire des couches avec les valeurs par défaut ajoutées
    """
    for layerID, layer in layers.items():
        # Ajoute la propriété key (utile pour l'entrée carto)
        layer['key'] = layerID
        if "producer" not in layer or len(layer["producer"]) == 0:
            layer["producer"] = ["Autres"]
        if "thematic" not in layer or len(layer["thematic"]) == 0:
            layer["thematic"] = ["Autres"]
        if "base" not in layer:
            layer["base"] = False
    return layers

def convert_thematic(layers, convert_table, verbose=False):
    # Conversion de la liste d'objets en dict {id: name}
    convert_dict = {item["id"]: item["name"] for item in convert_table}

    if convert_table:
        for layer in layers.values():
            thematics = layer.get("thematic", [])

            # Remplace chaque id de thématique par son nom si existant
            layer["thematic"] = [convert_dict.get(thematic, thematic) for thematic in thematics]

    return layers