import requests
from PIL import Image
from io import BytesIO
import xml.etree.ElementTree as ET
import numpy as np

class WMSThumbnailExtractor:
    def __init__(self, service_url, output_dir="thumbnails"):
        self.service_url = service_url
        self.output_dir = output_dir
        self.session = requests.Session()
        
        # Zones de zoom pour la France avec échelles
        # Échelles: pourcentage de réduction de la bbox
        self.france_zoom_levels = {
            0: {'name': 'France entière', 'bbox': (-5.5, 42, 8, 51.5)},
            1: {'name': 'France Nord', 'bbox': (-5.5, 48, 8, 51.5)},
            2: {'name': 'France Île-de-France', 'bbox': (1.5, 48, 3.5, 49.5)},
            3: {'name': 'France Ouest', 'bbox': (-5.5, 46, 0, 49)},
            4: {'name': 'France Centre', 'bbox': (-1, 45, 4, 48)},
            5: {'name': 'France Sud-Est', 'bbox': (3, 43, 8, 46)},
            6: {'name': 'France Sud-Ouest', 'bbox': (-5, 42, 2, 45)},
        }
        
        # Réductions d'échelle (pourcentage de la bbox à réduire)
        self.scale_reductions = [0, 10, 20, 30]  # 0%, 10%, 20%, 30% de réduction
        
    def get_wms_layers(self):
        """Récupère les couches disponibles du service WMS"""
        params = {
            'service': 'WMS',
            'version': '1.3.0',
            'request': 'GetCapabilities'
        }
        try:
            response = self.session.get(self.service_url, params=params, timeout=10)
            root = ET.fromstring(response.content)
            
            ns = {'wms': 'http://www.opengis.net/wms'}
            layers = []

            for layer in root.findall('.//wms:Layer', ns):
                name = layer.find('wms:Name', ns)
                title = layer.find('wms:Title', ns)
                
                if name is not None:
                    layers.append({
                        'name': name.text,
                        'title': title.text if title is not None else name.text,
                    })
            
            return layers
        except Exception as e:
            print(f"Erreur WMS: {e}")
            return []
    
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
    
    def extract_wms_thumbnail(self, layer_name, bbox, width=300, height=300, 
                             output_file=None, verbose=True):
        """
        Extrait une vignette d'une couche WMS
        """
        # Pour WMS 1.3.0, l'ordre est (miny, minx, maxy, maxx) au lieu de (minx, miny, maxx, maxy)
        bbox_str = f"{bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]}"
        
        params = {
            'service': 'WMS',
            'version': '1.3.0',
            'request': 'GetMap',
            'layers': layer_name,
            'bbox': bbox_str,
            'width': width,
            'height': height,
            'srs': 'EPSG:4326',
            'format': 'image/jpeg',
            'transparent': 'TRUE'
        }
        
        if verbose:
           print(f"  cfg : {params}")
        
        try:
            response = self.session.get(self.service_url, params=params, timeout=15)
            
            if response.status_code != 200 or not response.content or len(response.content) < 100:
                return None
            
            img = Image.open(BytesIO(response.content))
            
            # Vérifier le contenu
            has_content, message = self.has_visible_content(img)
            
            if not has_content:
                return None
            
            if output_file is None:
                output_file = f"{self.output_dir}/{layer_name.replace(':', '_')}.png"
            
            img.save(output_file)
            return output_file
            
        except Exception as e:
            if verbose:
                print(f"  ✗ Erreur: {e}")
            return None
    
    def try_france_zoom_levels(self, layer_name, verbose=True):
        """
        Essaie d'extraire une vignette avec plusieurs niveaux de zoom et échelles sur la France
        S'arrête dès qu'il trouve du contenu
        """
        print(f"\nCouche: {layer_name}")
        
        for zoom_level in sorted(self.france_zoom_levels.keys()):
            zone_info = self.france_zoom_levels[zoom_level]
            zone_name = zone_info['name']
            base_bbox = zone_info['bbox']
            
            # Essayer différentes échelles pour cette zone
            for scale_reduction in self.scale_reductions:
                bbox = self._apply_scale_reduction(base_bbox, scale_reduction)
                
                scale_str = f"échelle {100-scale_reduction}%" if scale_reduction > 0 else "échelle 100%"
                
                if verbose:
                    print(f"  Zoom {zoom_level}: {zone_name} - {scale_str}")
                
                output_file = f"{self.output_dir}/{layer_name}.png"
                
                result = self.extract_wms_thumbnail(
                    layer_name,
                    bbox=bbox,
                    width=300,
                    height=300,
                    output_file=output_file,
                    verbose=False
                )
                
                if result:
                    print(f"  ✓ Succès zoom {zoom_level} ({zone_name}) - {scale_str}")
                    return result
        
        print(f"  ✗ Aucun zoom/échelle n'a retourné du contenu")
        return None
    
    def _apply_scale_reduction(self, bbox, reduction_percent):
        """
        Applique une réduction d'échelle à une bbox
        reduction_percent: pourcentage de réduction (0-40%)
        """
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
        Extrait les vignettes de toutes les couches avec zoom progressif sur la France
        """
        layers = self.get_wms_layers()
        
        print(f"\n{'='*70}")
        print(f"URL - {self.service_url}")
        print(f"WMS - {len(layers)} couches trouvées")
        print(f"Stratégie: Zoom progressif sur la France")
        print(f"{'='*70}")
        
        success_count = 0
        fail_count = 0
        
        for layer in layers:  # layers[:20] Traiter les 20 premières couches
            result = self.try_france_zoom_levels(layer['name'], verbose=verbose)
            
            if result:
                success_count += 1
            else:
                fail_count += 1
        
        print(f"\n{'='*70}")
        print(f"Résultats: {success_count} vignettes générées, {fail_count} échecs")
        print(f"{'='*70}\n")

# Exemple d'utilisation
if __name__ == "__main__":
    import os
    
    os.makedirs("thumbnails-wms-v", exist_ok=True)
    
    # service WMS
    wms_url = "https://data.geopf.fr/wms-v"
    
    extractor = WMSThumbnailExtractor(wms_url)
    
    # Extraire avec zoom progressif sur la France
    extractor.extract_all_thumbnails(verbose=True)
