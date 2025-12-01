import json
import os
import re

# Chemins
json_path = "../dist/entreeCarto.json"
output_path = "./entreeCarto-test.json"
thumb_dirs = [
    "thumbnails-wms-r",
    "thumbnails-wms-v"
]

# URL de base GitHub
github_base = "https://raw.githubusercontent.com/IGNF/geoportal-configuration/refs/heads/new-url/extractor/"

# Suffixes à ignorer
suffixes = [
    r"\$GEOPORTAIL:OGC:WFS",
    r"\$GEOPORTAIL:OGC:WMS",
    r"\$GEOPORTAIL:OGC:WMTS",
    r"\$GEOPORTAIL:GPP:TMS"
]
suffix_pattern = re.compile("(" + "|".join(suffixes) + r")$")

def find_thumbnail(layer_name):
    # Retirer le suffixe si présent
    base_name = suffix_pattern.sub("", layer_name)
    for thumb_dir in thumb_dirs:
        for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
            thumb_path = os.path.join(thumb_dir, base_name + ext)
            if os.path.isfile(thumb_path):
                # Retourne l'URL GitHub
                return github_base + thumb_path
    return None

# Charger le JSON
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Ajouter le champ thumbnail
for layer in data.get("layers", {}).values():
    thumb = find_thumbnail(layer.get("name", ""))
    if thumb:
        layer["thumbnail"] = thumb

# Sauvegarder le JSON modifié dans un nouveau fichier
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)