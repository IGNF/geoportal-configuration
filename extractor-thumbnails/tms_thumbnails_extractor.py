import requests
from PIL import Image
from io import BytesIO
import xml.etree.ElementTree as ET
import os
import math

class TMSThumbnailExtractor:
    def __init__(self, service_url, output_dir="thumbnails-tms"):
        self.service_url = service_url
        self.output_dir = output_dir
        self.session = requests.Session()

    def get_tms_layers(self, verbose=False):
        """Récupère les couches TMS disponibles (exemple basique)"""
        try:
            response = self.session.get(self.service_url, timeout=10)
            root = ET.fromstring(response.content)
            layers = []
            for tilemap in root.findall(".//TileMap"):
                href = tilemap.attrib.get("href")
                # Extraction du nom de la couche depuis le href 
                # (ex: .../tms/1.0.0/COUCHE@EPSG:3857)
                if href:
                    name = href.rstrip('/').split('/')[-1]
                else:
                    name = "unknown"
                layers.append({"name": name, "href": href})
            
            if verbose:
                print(f"  --> {len(layers)} couches TMS trouvées")
                
            return layers
        except Exception as e:
            print(f"Erreur TMS: {e}")
            return []

    def extract_tms_tile(self, layer_href, zoom, x, y, verbose=False):
        """Extrait une tuile TMS individuelle"""
        tile_url = f"{layer_href}/{zoom}/{x}/{y}.png"
        if verbose:
            print(f"  --> Extraction tuile TMS: {tile_url}")
            
        try:
            response = self.session.get(tile_url, timeout=10)
            if response.status_code != 200 or not response.content or len(response.content) < 100:
                if verbose:
                    print(f"  --> Tuile TMS non disponible ou trop petite (code {response.status_code})")
                return None
            img = Image.open(BytesIO(response.content))
            return img
        except Exception as e:
            print(f"Erreur tuile TMS: {e}")
            return None

    def coord_to_tile(self, x, y, zoom, verbose=False):
        """
        Convertit des coordonnées EPSG:3857 (x, y) en indices de tuile TMS (col, row) pour un niveau de zoom donné.
        """
        # Taille du monde en EPSG:3857
        origin_shift = 20037508.342789244
        tile_size = 256

        # Nombre de tuiles à ce niveau de zoom
        num_tiles = 2 ** zoom

        # Calcul de la taille d'une tuile en mètres
        resolution = (2 * origin_shift) / tile_size / num_tiles

        # Colonne et ligne
        col = int((x + origin_shift) / (resolution * tile_size))
        row = int((origin_shift - y) / (resolution * tile_size))

        if verbose:
            print(f"  --> Coordonnées EPSG:3857 ({x}, {y}) → Zoom {zoom} → Tuile (col={col}, row={row})")
        
        return col, row
    
    def extract_simple_thumbnail(self, layer, bbox=None, verbose=True):
        # 1. Essayer plusieurs tuiles mondiales (zoom 0)
        zoom_world = 0
        world_tiles = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for col, row in world_tiles:
            img = self.extract_tms_tile(layer['href'], zoom_world, col, row, verbose=verbose)
            if img:
                img.save(f"{self.output_dir}/{layer['name']}.png")
                if verbose:
                    print(f"✓ Vignette mondiale extraite pour {layer['name']} (col={col}, row={row})")
                return True

        # 2. Essayer une tuile centrée sur la bbox de la donnée (si bbox fournie)
        if bbox:
            # Exemple : bbox = [minx, miny, maxx, maxy] en EPSG:3857
            zoom_bbox = 1
            # À adapter : calculer col/row à partir de la bbox et du zoom
            # Ici, on prend le centre de la bbox
            center_x = (bbox[0] + bbox[2]) / 2
            center_y = (bbox[1] + bbox[3]) / 2
            # À compléter : fonction pour convertir (center_x, center_y, zoom_bbox) en col/row
            col, row = self.coord_to_tile(center_x, center_y, zoom_bbox, verbose=verbose)
            img = self.extract_tms_tile(layer['href'], zoom_bbox, col, row, verbose=verbose)
            if img:
                img.save(f"{self.output_dir}/{layer['name']}.png")
                if verbose:
                    print(f"✓ Vignette bbox donnée extraite pour {layer['name']} (col={col}, row={row})")
                return True

        # 3. Essayer une tuile sur la France (zoom 5)
        france_bbox = [-612257.199, 5160979.444, 890555.926, 6710219.083]  # EPSG:3857
        zoom_france = 5
        center_x = (france_bbox[0] + france_bbox[2]) / 2
        center_y = (france_bbox[1] + france_bbox[3]) / 2
        col, row = self.coord_to_tile(center_x, center_y, zoom_france, verbose=verbose)
        img = self.extract_tms_tile(layer['href'], zoom_france, col, row, verbose=verbose)
        if img:
            img.save(f"{self.output_dir}/{layer['name']}.png")
            if verbose:
                print(f"✓ Vignette France extraite pour {layer['name']} (col={col}, row={row})")
            return True

        # 4. Essayer une tuile France zoomée (zoom 8)
        zoom_france_zoom = 8
        col, row = self.coord_to_tile(center_x, center_y, zoom_france_zoom, verbose=verbose)
        img = self.extract_tms_tile(layer['href'], zoom_france_zoom, col, row, verbose=verbose)
        if img:
            img.save(f"{self.output_dir}/{layer['name']}.png")
            if verbose:
                print(f"✓ Vignette France zoomée extraite pour {layer['name']} (col={col}, row={row})")
            return True

        if verbose:
            print(f"✗ Impossible d'extraire une vignette pertinente pour {layer['name']}")
        return False

    def extract_simple_all_thumbnails(self, verbose=False):
        layers = self.get_tms_layers(verbose=verbose)
        print(f"\n{'='*70}")
        print(f"URL - {self.service_url}")
        print(f"TMS - {len(layers)} couches trouvées")
        print(f"Stratégie: tuile mondiale → bbox donnée → tuile France")
        print(f"{'='*70}")

        os.makedirs(self.output_dir, exist_ok=True)
        
        success_count = 0
        fail_count = 0

        for layer in layers:
            output_file = f"{self.output_dir}/{layer['name']}.png"
            if os.path.exists(output_file):
                if verbose:
                    print(f"  file {layer['name']} already exist !")
                continue

            result = self.extract_simple_thumbnail(layer, verbose=verbose)
            if result:
                success_count += 1
            else:
                fail_count += 1

        print(f"\n{'='*70}")
        print(f"Résultats: {success_count} vignettes générées, {fail_count} échecs")
        print(f"{'='*70}\n")

# Exemple d'utilisation
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=False, default="thumbnails-tms")
    
    dir = parser.parse_args().dir
    
    tms_url = "https://data.geopf.fr/tms/1.0.0"
    extractor = TMSThumbnailExtractor(tms_url, output_dir=dir)
    extractor.extract_simple_all_thumbnails(verbose=True)