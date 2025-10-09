import json
import xml.etree.ElementTree as ET

from core.requester import getEdito, searchMtdUrls, getHeadRequest, getMetadata
from core.entree_carto.post_processes import filter_specific_duplicates, filter_layers, add_layers_default_values, convert_thematic
from core.entree_carto.merger import merge_edito, merge_service_de_recherche_infos

def generate_entree_carto_conf(merged_config):
    # Récupère les infos disponibles depuis le service recherche
    # en particulier "theme", "producers" et "thumbnail"
    mtd_urls_layers = searchMtdUrls()
    if mtd_urls_layers:
        merged_config = merge_service_de_recherche_infos(mtd_urls_layers, merged_config)
    # Récupère la configuration éditoriale
    edito = getEdito()
    if edito:
        merged_config = merge_edito(edito, merged_config)

    # Filtre couches
    merged_config["layers"] = filter_layers(merged_config["layers"])
    # Ajoute les valeurs par défaut
    merged_config["layers"] = add_layers_default_values(merged_config["layers"])
    # Filtre les couches WMS qui dupliquent une couche WMTS
    merged_config["layers"] = filter_specific_duplicates(merged_config["layers"])
    # Convertit les thématiques
    merged_config["layers"] = convert_thematic(merged_config["layers"], edito["topics"]["thematic"])
    # Sauvegarde le résultat
    with open("dist/entreeCarto.json", "w", encoding="utf-8") as file:
        file.writelines(json.dumps(merged_config, indent=2, ensure_ascii=False))
    return merged_config
