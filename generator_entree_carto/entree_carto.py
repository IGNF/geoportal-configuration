import json
import re
from time import sleep
from datetime import datetime


from core.requester import getEdito, searchMtdUrls
from core.post_processes import filter_specific_duplicates, filter_layers, add_layers_default_values, convert_thematic
from core.merger import merge_edito, merge_service_de_recherche_infos

def getTime(verbose=False):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(f"Current Time = , {current_time}")
    
"""
Creation du fichier entreeCarto.json à partir de fullConfig.json.
"""
class GenerateEntreeCarto:
    def __init__(self, count="full", output_path="entreeCarto-test.json", input_path="./dist/customConfig.json"):
        self.count = count
        self.output_path = output_path
        self.input_path = input_path

    def run(self, verbose=False):        
        """ 
        Génère le fichier entreeCarto.json à partir de fullConfig.json
        """
        getTime(verbose=verbose)
        
        # Charger le JSON
        with open(self.input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Prefixes à ignorer
        prefixes = [
            r"OGC:",
            r"GPP:"
        ]
        prefixes_pattern = re.compile("^(" + "|".join(prefixes) + r")")
        # Traitement des données pour créer entreeCarto.json
        if self.count != "full":
            data["layers"] = dict(list(data["layers"].items())[:int(self.count)])
            if verbose:
                print(f" --> Nombre de layers après limitation : {len(data['layers'])}")
        else:
            if verbose:
                print(f" --> Nombre de layers total : {len(data['layers'])}")

        layers_name = ""
        counter = 1
        for service in ["WMTS", "WMS", "TMS", "WFS"]:
            if verbose:
                print(f" --> Traitement des couches de type : {service} ")
            for layer in data.get("layers", {}).values():
                if 'serviceParams' not in layer or 'id' not in layer['serviceParams']:
                    continue
                # Retirer le préfixe si présent
                service_name = prefixes_pattern.sub("", layer['serviceParams']['id'])
                if service_name != service:
                    continue
                if verbose:
                    print(f"--> layer ({counter}) : {layer['name']} / {service}")
                # Creation de la chaine des noms de couches
                if layers_name:
                    layers_name += "|" + layer['name']
                else:
                    layers_name = layer['name']
                if counter % 20 == 0:
                    # Récupère les infos disponibles depuis le service recherche
                    # en particulier "theme", "producers" et "thumbnail"
                    mtd_urls_layers = searchMtdUrls(layers_name, service, verbose=verbose)
                    if mtd_urls_layers:
                        data = merge_service_de_recherche_infos(mtd_urls_layers, data, verbose=verbose)
                    if verbose:
                        print(f" --> Couches traitées : {counter} / {len(data['layers'])} ")
                    layers_name = ""
                    # sleep(1)  # Pour ne pas surcharger le service de recherche
                counter += 1
            # Traite les couches restantes
            if layers_name:
                mtd_urls_layers = searchMtdUrls(layers_name, service, verbose=verbose)
                if mtd_urls_layers:
                    data = merge_service_de_recherche_infos(mtd_urls_layers, data, verbose=verbose)
                if verbose:
                    print(f" --> Couches traitées : {counter - 1} / {len(data['layers'])} ")
                layers_name = ""
                # sleep(1)  # Pour ne pas surcharger le service de recherche
              
        # Récupère la configuration éditoriale
        edito = getEdito()
        if edito:
            data = merge_edito(edito, data, verbose=verbose)

        # Filtre couches
        data["layers"] = filter_layers(data["layers"], verbose=verbose)
        # Ajoute les valeurs par défaut
        data["layers"] = add_layers_default_values(data["layers"], verbose=verbose)
        # Filtre les couches WMS qui dupliquent une couche WMTS
        data["layers"] = filter_specific_duplicates(data["layers"], verbose=verbose)
        # Convertit les thématiques
        data["layers"] = convert_thematic(data["layers"], edito["topics"]["thematic"], verbose=verbose)

        getTime(verbose=verbose)
        
        # Sauvegarder le JSON modifié dans un nouveau fichier
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return data
    
# Exemple d'utilisation
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=False, default="./dist/customConfig.json")
    parser.add_argument("--output", required=False, default="entreeCarto-test.json")
    parser.add_argument("--count", required=False, default="full")
    
    input = parser.parse_args().input
    output = parser.parse_args().output
    count = parser.parse_args().count
    
    generator = GenerateEntreeCarto(
        count=count,
        input_path=input,
        output_path=output
    )
    generator.run(verbose=True)