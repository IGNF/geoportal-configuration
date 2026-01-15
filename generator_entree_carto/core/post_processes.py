def filter_layers(layers_dict, verbose=False):
    """
    Filtre les couches dans un dictionnaire en fonction de conditions données.
    Ce code sélectionne uniquement les couches 
    - dont la projection n’est pas LAMB93 ou EPSG:2154 et 
    - dont le type de service est WMTS, WMS ou TMS.
    
    Args:
        layers_dict (dict): Dictionnaire des couches à filtrer
    
    Returns:
        dict: Dictionnaire des couches filtrées
    """
    if verbose:
        print(" --> Filtrage des couches selon projection et type de service ")
    
    filtered_layers = {}

    for layer_id, layer in layers_dict.items():
        # Vérifie la projection
        projection = layer.get("defaultProjection", "")
        if "IGNF:LAMB93" in projection or "EPSG:2154" in projection:
            if "WMS" not in layer.get("serviceParams", {}).get("id", ""):
                if verbose:
                    print(f"Exclusion {layer_id} : projection {projection}")
                continue

        # Vérifie le type de service
        service_params = layer.get("serviceParams", {})
        service_id = service_params.get("id", "") if isinstance(service_params, dict) else ""
        if not any(s in service_id for s in ["WMTS", "WMS", "TMS"]):
            if verbose:
                print(f"Exclusion {layer_id} : service {service_id}")
            continue

        # Si les deux conditions sont OK, on garde la couche
        filtered_layers[layer_id] = layer

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
    if verbose:
        print(" --> Filtrage des couches WMS dupliquant une couche WMTS ")
        
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
            if verbose:
                for k in info['wms_keys']:
                    print(f"Suppression de la couche WMS dupliquée : {k} (base_name={base_name})")
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
    if verbose:
        print(" --> Ajout des valeurs par défaut aux couches ")
        
    for layerID, layer in layers.items():
        # Ajoute la propriété key (utile pour l'entrée carto)
        layer['key'] = layerID
        if "producer" not in layer or len(layer["producer"]) == 0 or layer["producer"] == [""]:
            layer["producer"] = ["Autres"]
            if verbose:
                print(f"Ajout du producteur par défaut pour la couche {layerID}")
        if "thematic" not in layer or len(layer["thematic"]) == 0 or layer["thematic"] == [""]:
            layer["thematic"] = ["Autres"]
            if verbose:
                print(f"Ajout de la thématique par défaut pour la couche {layerID}")
        if "base" not in layer:
            layer["base"] = False
    return layers

def convert_thematic(layers, convert_table, verbose=False):
    """
    Remplace les identifiants de thématiques par leur nom dans chaque couche.

    Args:
        layers (dict): Dictionnaire des couches à traiter
        convert_table (list): Liste d'objets {"id": ..., "name": ...} pour la conversion
        verbose (bool): Affiche les infos de conversion si True

    Returns:
        dict: Dictionnaire des couches avec les thématiques converties
    """
    # Conversion de la liste d'objets en dict {id: name}
    convert_dict = {item["id"]: item["name"] for item in convert_table}
    if verbose:
        print(f" --> Dictionnaire de conversion des thématiques : {convert_dict}")
        
    if convert_table:
        # Pour chaque couche, remplacer les ids par les noms
        for layer_id, layer in layers.items():
            thematics = layer.get("thematic", [])
            converted_thematics = []
            for t in thematics:
                if t in convert_dict:
                    converted_thematics.append(convert_dict[t])
                else:
                    converted_thematics.append(t)
                    if verbose:
                        print(f"Attention : thématique '{t}' non trouvée pour la couche {layer_id}")
            layer["thematic"] = converted_thematics
            if verbose:
                print(f"Couche {layer_id} : thématiques converties -> {layer['thematic']}")
    return layers