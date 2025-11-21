import requests
from PIL import Image
from io import BytesIO
import xml.etree.ElementTree as ET
import numpy as np

class WMSWMTSThumbnailExtractor:
    def __init__(self, service_url, output_dir="thumbnails"):
        self.service_url = service_url
        self.output_dir = output_dir
        self.session = requests.Session()
        
        # Zones de zoom pour la France avec échelles
        # Coordonnées en Web Mercator (EPSG:3857)
        self.france_zoom_levels = {
            0: {'name': 'France entière', 'bbox': (-612257.199, 5160979.444, 890555.926, 6710219.083)},
            1: {'name': 'France Nord', 'bbox': (-612257.199, 6106854.835, 890555.926, 6710219.083)},
            2: {'name': 'France Île-de-France', 'bbox': (166979.236, 6106854.835, 389618.218, 6360130.741)},
            3: {'name': 'France Ouest', 'bbox': (-612257.199, 5780349.220, 0.000, 6274861.394)},
            4: {'name': 'France Centre', 'bbox': (-111319.491, 5621521.486, 445277.963, 6106854.835)},
            5: {'name': 'France Sud-Est', 'bbox': (333958.472, 5311971.847, 890555.926, 5780349.220)},
            6: {'name': 'France Sud-Ouest', 'bbox': (-556597.454, 5160979.444, 222638.982, 5621521.486)},
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
                
                # Récupérer la bbox (EX_GeographicBoundingBox ou BoundingBox)
                bbox = None
                bbox_elem = layer.find('wms:EX_GeographicBoundingBox', ns)
                if bbox_elem is None:
                    bbox_elem = layer.find('wms:BoundingBox', ns)
                
                if bbox_elem is not None:
                    try:
                        if bbox_elem.tag.endswith('EX_GeographicBoundingBox'):
                            minx = float(bbox_elem.find('wms:westBoundLongitude', ns).text)
                            miny = float(bbox_elem.find('wms:southBoundLatitude', ns).text)
                            maxx = float(bbox_elem.find('wms:eastBoundLongitude', ns).text)
                            maxy = float(bbox_elem.find('wms:northBoundLatitude', ns).text)
                        else:
                            minx = float(bbox_elem.get('minx', -180))
                            miny = float(bbox_elem.get('miny', -90))
                            maxx = float(bbox_elem.get('maxx', 180))
                            maxy = float(bbox_elem.get('maxy', 90))
                        
                        # Valider si ce n'est pas l'étendue mondiale
                        if minx != -180 or maxx != 180:
                            # Convertir WGS84 en Web Mercator
                            bbox = self._wgs84_to_mercator(minx, miny, maxx, maxy)
                    except:
                        pass
                
                if name is not None:
                    layers.append({
                        'name': name.text,
                        'title': title.text if title is not None else name.text,
                        'bbox': bbox
                    })
            
            print(f"  → {len(layers)} couches WMS détectées")
            return layers
        except Exception as e:
            print(f"Erreur WMS: {e}")
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
    
    def extract_wms_thumbnail(self, layer_name, bbox, width=300, height=300, 
                             output_file=None, verbose=True):
        """
        Extrait une vignette d'une couche WMS
        """
        # Pour WMS 1.3.0, l'ordre est (miny, minx, maxy, maxx) au lieu de (minx, miny, maxx, maxy)
        bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
        
        params = {
            'service': 'WMS',
            'version': '1.3.0',
            'request': 'GetMap',
            'layers': layer_name,
            'bbox': bbox_str,
            'width': width,
            'height': height,
            'crs': 'EPSG:3857',
            'format': 'image/png',
            'transparent': 'TRUE',
            'styles': ''
        }
        
        try:
            response = self.session.get(self.service_url, params=params, timeout=15)
            
            # Vérifier erreur WMS
            if response.headers.get('Content-Type', '').startswith("text/xml"):
                # Problème côté serveur
                try:
                    print("\n=== Erreur WMS ===")
                    print(response.text)
                except:
                    pass
                return None
            
            if response.status_code != 200 or not response.content or len(response.content) < 100:
                return None
            
            img = Image.open(BytesIO(response.content))
            
            # Vérifier le contenu
            has_content, message = self.has_visible_content(img)
            
            if not has_content:
                return None
            
            if output_file is None:
                output_file = f"{self.output_dir}/{layer_name}.png"
            
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
        print(f"WMS - {len(layers)} couches trouvées")
        print(f"Stratégie: Zoom progressif sur la France")
        print(f"{'='*70}")
        
        success_count = 0
        fail_count = 0
        
        for layer in layers[:20]:  # Traiter les 20 premières couches
            self.debug_single_request(
                layer['name'],
                self.france_zoom_levels[0]['bbox']
            )
            result = self.try_france_zoom_levels(layer['name'], verbose=verbose)
            
            if result:
                success_count += 1
            else:
                fail_count += 1
        
        print(f"\n{'='*70}")
        print(f"Résultats: {success_count} vignettes générées, {fail_count} échecs")
        print(f"{'='*70}\n")

    def debug_extract_all_thumbnails(self, verbose=True):
        """
        Extrait les vignettes de toutes les couches sans zoom progressif
        """
        layers = self.get_wms_layers()
        
        print(f"\n{'='*70}")
        print(f"URL - {self.service_url}")
        print(f"WMS - {len(layers)} couches trouvées")
        print(f"Stratégie: None")
        print(f"{'='*70}")
        
        success_count = 0
        
        for layer in layers:  # layers[:20] Traiter les 20 premières couches
            self.debug_single_request(
                layer['name'],
                self.france_zoom_levels[0]['bbox']
            )
            
            success_count += 1
        
        print(f"\n{'='*70}")
        print(f"Résultats: {success_count} vignettes générées")
        print(f"{'='*70}\n")
        
    def debug_single_request(self, layer_name, bbox, width=300, height=300):
        """Effectue une requête GetMap brute et affiche la réponse ou l’erreur WMS"""
        
        bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"  # EPSG:3857
        
        params = {
            'service': 'WMS',
            'version': '1.3.0',
            'request': 'GetMap',
            'layers': layer_name,
            'bbox': bbox_str,
            'width': width,
            'height': height,
            'crs': 'EPSG:3857',
            'styles': '',
            'format': 'image/png',
            'transparent': 'TRUE'
        }

        print(f"→ Requête sur {layer_name}")
        print(params)

        if os.path.exists(f"thumbnails-wms-r/{layer_name}.png"):
            print("  ✓ Vignette déjà extraite, passage.")
            return
        
        response = self.session.get(self.service_url, params=params, timeout=15)

        print(f"HTTP code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")

        # Si la réponse est XML, c’est probablement une exception WMS
        if response.headers.get('Content-Type', '').startswith("text/xml"):
            print("\n===== Erreur WMS détectée =====")
            print(response.text)
            return

        # Sinon on tente d’afficher quelques infos
        print(f"Image reçue ({len(response.content)} octets)")
        
        try:
            img = Image.open(BytesIO(response.content))
            print(f"→ Image OK : {img.size}  {img.mode}")
            img.save(f"thumbnails-wms-r/{layer_name}.png")
        except Exception as e:
            print(f"Impossible de lire l’image : {e}")

# Exemple d'utilisation
if __name__ == "__main__":
    import os
    
    os.makedirs("thumbnails-wms-r", exist_ok=True)
    
    # Exemple avec un service WMS (Géoportail français)
    wms_url = "https://data.geopf.fr/wms-r"
    
    extractor = WMSWMTSThumbnailExtractor(wms_url)
    
    # extractor.debug_single_request(
    # 	"ADMINEXPRESS-COG-CARTO-PE.2025", # "CADASTRALPARCELS.PARCELS",
    # 	extractor.france_zoom_levels[0]['bbox']
    # )

    # Extraire avec zoom progressif sur la France
    # extractor.extract_all_thumbnails(verbose=True)
    extractor.debug_extract_all_thumbnails(verbose=True)
