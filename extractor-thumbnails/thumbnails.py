import json
import os
import re

"""
Mise à jour du fichier entreeCarto.json pour ajouter les miniatures aux couches.
"""
class UpdateThumbnails:
    def __init__(self, github_base, output_path="entreeCarto.json", input_path="entreeCarto-test.json"):
        self.github_base = github_base
        self.output_path = output_path
        self.input_path = input_path
    
    def run(self, verbose=False):
        # Charger le JSON
        with open(self.input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Ajouter le champ thumbnail
        for layer in data.get("layers", {}).values():
            thumb = self.find_thumbnail(layer.get("name", ""), verbose=verbose)
            if thumb is not None and layer.get("thumbnail", "") == "":
                layer["thumbnail"] = thumb

        # Sauvegarder le JSON modifié dans un nouveau fichier
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
    def find_thumbnail(self, layer_name, verbose=False):
        # Directoires de miniatures
        thumb_dirs = [
            "thumbnails-wms-r",
            "thumbnails-wms-v",
            "thumbnails-wmts",
            "thumbnails-tms"
        ]

        # Suffixes à ignorer
        suffixes = [
            r"\$GEOPORTAIL:OGC:WFS",
            r"\$GEOPORTAIL:OGC:WMS",
            r"\$GEOPORTAIL:OGC:WMTS",
            r"\$GEOPORTAIL:GPP:TMS"
        ]
        suffix_pattern = re.compile("(" + "|".join(suffixes) + r")$")
        
        # Retirer le suffixe si présent
        base_name = suffix_pattern.sub("", layer_name)
        for thumb_dir in thumb_dirs:
            for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
                thumb_path_str = os.path.join(thumb_dir, base_name + ext)
                thumb_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), thumb_dir, base_name + ext)
                if os.path.isfile(thumb_path):
                    if verbose:
                        print(f" --> found : {thumb_path_str}")
                    # Retourne l'URL GitHub
                    return self.github_base + thumb_path_str
        return None

# Exemple d'utilisation
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=False, default="entreeCarto-test.json")
    parser.add_argument("--output", required=False, default="entreeCarto.json")
    
    input = parser.parse_args().input
    output = parser.parse_args().output
    
    updater = UpdateThumbnails(
        github_base="https://raw.githubusercontent.com/IGNF/geoportal-configuration/refs/heads/new-url/extractor-thumbnails/",
        output_path=output,
        input_path=input
    )
    # Lancer la mise à jour des miniatures
    updater.run(True)