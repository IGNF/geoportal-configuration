import requests
from PIL import Image
from io import BytesIO
import xml.etree.ElementTree as ET
import numpy as np

class WMTSThumbnailExtractor:
    def __init__(self, service_url, output_dir="thumbnails-wmts"):
        self.service_url = service_url
        self.output_dir = output_dir
        self.session = requests.Session()
        
        # Zones de zoom pour la France en Web Mercator (EPSG:3857)
        # Mêmes zones que WMS mais en coordonnées projetées
        self.france_zoom_levels = {
            0: {'name': 'France entière', 'bbox': (-612257.199, 5160979.444, 890555.926, 6710219.083)},
            1: {'name': 'France Nord', 'bbox': (-612257.199, 6106854.835, 890555.926, 6710219.083)},
            2: {'name': 'France Île-de-France', 'bbox': (166979.236, 6106854.835, 389618.218, 6360130.741)},
            3: {'name': 'France Ouest', 'bbox': (-612257.199, 5780349.220, 0.000, 6274861.394)},
            4: {'name': 'France Centre', 'bbox': (-111319.491, 5621521.486, 445277.963, 6106854.835)},
            5: {'name': 'France Sud-Est', 'bbox': (333958.472, 5311971.847, 890555.926, 5780349.220)},
            6: {'name': 'France Sud-Ouest', 'bbox': (-556597.454, 5160979.444, 222638.982, 5621521.486)},
        }
        
        # Réductions d'échelle
        self.scale_reductions = [0, 10, 20, 30, 40, 50]
        
        # Niveaux de zoom WMTS à tester
        self.wmts_zoom_levels = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        
    def get_wmts_layers(self):
        """Récupère les couches disponibles du service WMTS avec leurs bbox"""
        params = {
            'service': 'WMTS',
            'version': '1.0.0',
            'request': 'GetCapabilities'
        }
        try:
            response = self.session.get(self.service_url, params=params, timeout=10)
            root = ET.fromstring(response.content)
            
            layers = []
            
            # Namespaces pour GeoPF
            wmts_ns = 'http://www.opengis.net/wmts/1.0'
            ows_ns = 'http://www.opengis.net/ows/1.1'
            
            # Trouver l'élément Contents
            contents = root.find(f'{{{wmts_ns}}}Contents')
            if contents is None:
                print(f"  ✗ Élément Contents non trouvé")
                return []
            
            # Parcourir les Layer dans Contents
            for layer in contents.findall(f'{{{wmts_ns}}}Layer'):
                identifier = layer.find(f'{{{ows_ns}}}Identifier')
                title = layer.find(f'{{{ows_ns}}}Title')
                mime_type = layer.find(f'{{{wmts_ns}}}Format')
                
                # Récupérer la bbox (WGS84BoundingBox)
                bbox = None
                bbox_elem = layer.find(f'{{{ows_ns}}}WGS84BoundingBox')
                if bbox_elem is not None:
                    try:
                        lower_corner = bbox_elem.find(f'{{{ows_ns}}}LowerCorner')
                        upper_corner = bbox_elem.find(f'{{{ows_ns}}}UpperCorner')
                        
                        if lower_corner is not None and upper_corner is not None:
                            lower_text = lower_corner.text.strip().split()
                            upper_text = upper_corner.text.strip().split()
                            
                            minx = float(lower_text[0])
                            miny = float(lower_text[1])
                            maxx = float(upper_text[0])
                            maxy = float(upper_text[1])
                            
                            # Convertir WGS84 en Web Mercator
                            bbox = self._wgs84_to_mercator(minx, miny, maxx, maxy)
                    except Exception as e:
                        print(f"  Erreur lecture bbox: {e}")
                        bbox = None
                
                # Récupérer les TileMatrixSet disponibles
                tile_matrix_sets = []
                for tms_link in layer.findall(f'{{{wmts_ns}}}TileMatrixSetLink'):
                    tms = tms_link.find(f'{{{wmts_ns}}}TileMatrixSet')
                    if tms is not None and tms.text:
                        tile_matrix_sets.append(tms.text)
                
                if identifier is not None and identifier.text:
                    layers.append({
                        'name': identifier.text,
                        'title': title.text if title is not None else identifier.text,
                        'mime_type': mime_type.text,
                        'tile_matrix_sets': tile_matrix_sets,
                        'bbox': bbox
                    })
            
            print(f"  → {len(layers)} couches WMTS détectées")
            
            return layers
        except Exception as e:
            print(f"Erreur WMTS: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _wgs84_to_mercator(self, minx, miny, maxx, maxy):
        """Convertit une bbox WGS84 en Web Mercator (EPSG:3857)"""
        import math
        
        EARTH_RADIUS = 20037508.34
        
        def lnglat_to_merc(lng, lat):
            x = lng * EARTH_RADIUS / 180.0
            y = math.log(math.tan((90.0 + lat) * math.pi / 360.0)) * EARTH_RADIUS
            return x, y
        
        merc_minx, merc_maxy = lnglat_to_merc(minx, maxy)
        merc_maxx, merc_miny = lnglat_to_merc(maxx, miny)
        
        return (merc_minx, merc_miny, merc_maxx, merc_maxy)
    
    def has_visible_content(self, image):
        """Vérifie si l'image contient du contenu visible"""
        img_array = np.array(image.convert('RGB'))
        
        # Analyser la variance des couleurs
        gray = 0.299 * img_array[:, :, 0] + 0.587 * img_array[:, :, 1] + 0.114 * img_array[:, :, 2]
        variance = np.var(gray)
        
        # Vérifier la distribution des pixels
        unique_colors = len(np.unique(img_array.reshape(-1, 3), axis=0))
        
        if variance < 30:
            return False, f"Variance très faible ({variance:.1f})"
        
        if unique_colors < 5:
            return False, f"Très peu de couleurs ({unique_colors})"
        
        return True, f"Image avec contenu (variance: {variance:.1f})"
    
    def bbox_to_tile_coords(self, bbox, zoom_level):
        """
        Convertit une bounding box Web Mercator (EPSG:3857) en coordonnées de tuiles WMTS
        Retourne les min/max row et col pour le niveau de zoom
        """
        minx, miny, maxx, maxy = bbox
        
        # Web Mercator projection bounds (EPSG:3857)
        EARTH_RADIUS = 20037508.34
        
        def merc_to_tile(x, y, z):
            """Convertir coordonnées Mercator en tuile"""
            n = 2.0 ** z
            tile_x = int((x + EARTH_RADIUS) / (2 * EARTH_RADIUS) * n)
            tile_y = int((EARTH_RADIUS - y) / (2 * EARTH_RADIUS) * n)
            return tile_x, tile_y
        
        # Convertir en coordonnées de tuiles
        tile_minx, tile_maxy = merc_to_tile(minx, maxy, zoom_level)
        tile_maxx, tile_miny = merc_to_tile(maxx, miny, zoom_level)
        
        return {
            'col_min': tile_minx,
            'col_max': tile_maxx,
            'row_min': tile_miny,
            'row_max': tile_maxy
        }
    
    def extract_wmts_tile(self, layer_name, mime_type, tile_matrix_set, col, row, zoom, 
                         output_file=None, verbose=True):
        """
        Extrait une tuile WMTS individuelle (256x256 pixels)
        """
        params = {
            'service': 'WMTS',
            'version': '1.0.0',
            'request': 'GetTile',
            'layer': layer_name,
            'style': 'normal',
            'tilematrixset': tile_matrix_set,
            'tilematrix': zoom,
            'tilerow': row,
            'tilecol': col,
            'format': mime_type
        }
        
        try:
            response = self.session.get(self.service_url, params=params, timeout=15)
            
            if response.status_code != 200 or not response.content or len(response.content) < 100:
                return None
            
            img = Image.open(BytesIO(response.content))
            
            # Vérifier le contenu
            has_content, message = self.has_visible_content(img)
            
            if not has_content:
                return None
            
            if output_file:
                img.save(output_file)
            
            return img
            
        except Exception as e:
            if verbose:
                print(f"  ✗ Erreur tuile: {e}")
            return None
    
    def extract_wmts_thumbnail_for_zone(self, layer_name, mime_type, tile_matrix_set, bbox, 
                                       zoom_level, output_file=None, verbose=True):
        """
        Extrait une vignette WMTS pour une zone donnée en combinant plusieurs tuiles
        """
        try:
            # Obtenir les coordonnées de tuiles
            tile_coords = self.bbox_to_tile_coords(bbox, zoom_level)
            
            col_min = tile_coords['col_min']
            col_max = tile_coords['col_max']
            row_min = tile_coords['row_min']
            row_max = tile_coords['row_max']
            
            # Limiter à 4 tuiles maximum (2x2)
            col_max = min(col_min + 1, col_max)
            row_max = min(row_min + 1, row_max)
            
            # Récupérer les tuiles
            tiles = {}
            for col in range(col_min, col_max + 1):
                for row in range(row_min, row_max + 1):
                    tile_img = self.extract_wmts_tile(
                        layer_name, mime_type, tile_matrix_set, col, row, zoom_level,
                        verbose=False
                    )
                    if tile_img:
                        tiles[(col, row)] = tile_img
                    else:
                        return None  # Si une tuile manque, abandonner
            
            if not tiles:
                return None
            
            # Assembler les tuiles en une image
            if len(tiles) == 1:
                combined_img = list(tiles.values())[0]
            else:
                # Créer une image assemblée
                tile_width = 256
                combined_width = (col_max - col_min + 1) * tile_width
                combined_height = (row_max - row_min + 1) * tile_width
                
                combined_img = Image.new('RGB', (combined_width, combined_height))
                
                for (col, row), tile in tiles.items():
                    x = (col - col_min) * tile_width
                    y = (row - row_min) * tile_width
                    combined_img.paste(tile, (x, y))
            
            # Redimensionner à 300x300
            combined_img = combined_img.resize((300, 300), Image.Resampling.LANCZOS)
            
            if output_file:
                combined_img.save(output_file)
            
            return output_file
            
        except Exception as e:
            if verbose:
                print(f"  ✗ Erreur extraction: {e}")
            return None
    
    def try_france_zoom_levels_wmts(self, layer_name, mime_type, tile_matrix_set, verbose=True):
        """
        Essaie d'extraire une vignette WMTS avec plusieurs niveaux de zoom et échelles sur la France
        """
        print(f"\nCouche: {layer_name}")
        
        for zone_level in sorted(self.france_zoom_levels.keys()):
            zone_info = self.france_zoom_levels[zone_level]
            zone_name = zone_info['name']
            base_bbox = zone_info['bbox']
            
            # Essayer différentes échelles pour cette zone
            for scale_reduction in self.scale_reductions:
                bbox = self._apply_scale_reduction(base_bbox, scale_reduction)
                scale_str = f"échelle {100-scale_reduction}%" if scale_reduction > 0 else "échelle 100%"
                
                # Essayer différents niveaux de zoom WMTS
                for wmts_zoom in self.wmts_zoom_levels:
                    if verbose:
                        print(f"  Zone {zone_level} ({zone_name}) - {scale_str} - WMTS zoom {wmts_zoom}")
                    
                    output_file = f"{self.output_dir}/{layer_name}.png"
                    if os.path.exists(output_file):
                      print(f"  file {layer_name} already exist !")
                      continue
                    
                    result = self.extract_wmts_thumbnail_for_zone(
                        layer_name, mime_type, tile_matrix_set, bbox, wmts_zoom,
                        output_file=output_file,
                        verbose=False
                    )
                    
                    if result:
                        print(f"  ✓ Succès zone {zone_level} ({zone_name}) - {scale_str} - WMTS zoom {wmts_zoom}")
                        return result
        
        print(f"  ✗ Aucune combinaison n'a retourné du contenu")
        return None
    
    def _apply_scale_reduction(self, bbox, reduction_percent):
        """Applique une réduction d'échelle à une bbox"""
        minx, miny, maxx, maxy = bbox
        width = maxx - minx
        height = maxy - miny
        
        reduction = reduction_percent / 100.0
        
        new_minx = minx + width * reduction / 2
        new_miny = miny + height * reduction / 2
        new_maxx = maxx - width * reduction / 2
        new_maxy = maxy - height * reduction / 2
        
        return (new_minx, new_miny, new_maxx, new_maxy)
    
    def extract_all_thumbnails(self, verbose=True):
        """
        Extrait les vignettes de toutes les couches WMTS
        """
        layers = self.get_wmts_layers()
        
        print(f"\n{'='*70}")
        print(f"URL - {self.service_url}")
        print(f"WMTS - {len(layers)} couches trouvées")
        print(f"Stratégie: Bbox couche (GetCapabilities) → Zones France prédéfinies")
        print(f"{'='*70}")
        
        success_count = 0
        fail_count = 0
        
        for layer in layers:
            output_file = f"{self.output_dir}/{layer['name']}.png"
            if os.path.exists(output_file):
                print(f"  file {layer['name']} already exist !")
                continue
             
            # Utiliser le premier TileMatrixSet disponible
            if layer['tile_matrix_sets']:
                tile_matrix_set = layer['tile_matrix_sets'][0]
                
                # Essayer d'abord avec la bbox de la couche si disponible
                if layer['bbox']:
                    print(f"\nCouche: {layer['name']}")
                    print(f"  → Bbox détectée dans GetCapabilities: {layer['bbox']}")
                    
                    result = self._try_layer_bbox_wmts(
                        layer['name'], layer['mime_type'], tile_matrix_set, layer['bbox'], verbose=verbose
                    )
                    
                    if result:
                        print(f"  ✓ Vignette générée avec bbox de la couche")
                        success_count += 1
                    else:
                        # Fallback: stratégie par défaut France
                        print(f"  → Fallback sur zones France prédéfinies...")
                        result = self.try_france_zoom_levels_wmts(
                            layer['name'], layer['mime_type'], tile_matrix_set, verbose=False
                        )
                        
                        if result:
                            success_count += 1
                        else:
                            fail_count += 1
                else:
                    # Pas de bbox: stratégie France directement
                    result = self.try_france_zoom_levels_wmts(
                        layer['name'], layer['mime_type'], tile_matrix_set, verbose=verbose
                    )
                    
                    if result:
                        success_count += 1
                    else:
                        fail_count += 1
            else:
                print(f"\nCouche: {layer['name']}")
                print(f"  ✗ Aucun TileMatrixSet disponible")
                fail_count += 1
        
        print(f"\n{'='*70}")
        print(f"Résultats: {success_count} vignettes générées, {fail_count} échecs")
        print(f"{'='*70}\n")
    
    def _try_layer_bbox_wmts(self, layer_name, mime_type, tile_matrix_set, bbox, verbose=True):
        """
        Essaie d'extraire une vignette en utilisant la bbox de la couche
        """
        # Essayer avec différentes échelles
        for scale_reduction in [0, 10, 20, 30, 40, 50]:
            scaled_bbox = self._apply_scale_reduction(bbox, scale_reduction)
            scale_str = f"échelle {100-scale_reduction}%" if scale_reduction > 0 else "échelle 100%"
            
            # Essayer avec différents niveaux WMTS
            for wmts_zoom in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
                if verbose:
                    print(f"  Bbox couche - {scale_str} - WMTS zoom {wmts_zoom}")
                
                output_file = f"{self.output_dir}/{layer_name}.png"
                if os.path.exists(output_file):
                  print(f"  file {layer_name} already exist !")
                  continue
                
                result = self.extract_wmts_thumbnail_for_zone(
                    layer_name, mime_type, tile_matrix_set, scaled_bbox, wmts_zoom,
                    output_file=output_file,
                    verbose=False
                )
                
                if result:
                    print(f"  ✓ Succès avec bbox couche - {scale_str} - WMTS zoom {wmts_zoom}")
                    return result
        
        return None

# Exemple d'utilisation
if __name__ == "__main__":
    import os
    
    os.makedirs("thumbnails-wmts", exist_ok=True)
    
    # Service WMTS - Géoportail France
    wmts_url = "https://data.geopf.fr/wmts"
    
    extractor = WMTSThumbnailExtractor(wmts_url)
    
    # Extraire avec zoom progressif sur la France
    extractor.extract_all_thumbnails(verbose=True)
