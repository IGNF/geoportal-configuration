import xml.etree.ElementTree as ET
from core.requester import getMetadata
import requests
import struct
from core.requester import getHeadRequest

def get_image_dimensions(url: str):
    # --- Étape 1 : HEAD pour connaître le type ---
    header = getHeadRequest(url)
    content_type = header["content-type"].lower()

    # --- Étape 2 : choisir max_bytes selon le type ---
    if "png" in content_type:
        max_bytes = 100       # PNG : très peu d’octets nécessaires
    elif "gif" in content_type:
        max_bytes = 100       # GIF : idem
    elif "jpeg" in content_type or "jpg" in content_type:
        max_bytes = 8192      # JPEG : peut contenir des métadonnées → plus gros
    elif "webp" in content_type:
        max_bytes = 300       # WebP : info souvent très proche du début
    else:
        max_bytes = 16384     # Par défaut : 16 Ko pour sécurité

    # --- Étape 3 : GET partiel ---
    headers = {"Range": f"bytes=0-{max_bytes-1}"}
    resp = requests.get(url, headers=headers)
    if resp.status_code not in (200, 206):
        raise Exception(f"HTTP {resp.status_code} lors du GET partiel")
    
    data = resp.content

    # --- Étape 4 : parser dimensions ---
    # PNG
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        width, height = struct.unpack(">II", data[16:24])
        return {"format": "png", "width": width, "height": height}

    # GIF
    if data.startswith((b"GIF87a", b"GIF89a")):
        width, height = struct.unpack("<HH", data[6:10])
        return {"format": "gif", "width": width, "height": height}

    # JPEG
    if data[0:2] == b"\xff\xd8":
        offset = 2
        while offset < len(data):
            if data[offset] != 0xFF:
                offset += 1
                continue
            marker = data[offset + 1]
            length = struct.unpack(">H", data[offset+2:offset+4])[0]
            if 0xC0 <= marker <= 0xC3:
                height, width = struct.unpack(">HH", data[offset+5:offset+9])
                return {"format": "jpeg", "width": width, "height": height}
            offset += 2 + length
        raise Exception("JPEG : dimensions non trouvées, il faut augmenter max_bytes")

    # WebP
    if data[0:4] == b"RIFF" and data[8:12] == b"WEBP":
        chunk = data[12:16]
        if chunk == b"VP8 ":
            width, height = struct.unpack("<HH", data[26:30])
            width &= 0x3FFF
            height &= 0x3FFF
            return {"format": "webp", "width": width, "height": height}
        elif chunk == b"VP8X":
            width = 1 + int.from_bytes(data[24:27], "little")
            height = 1 + int.from_bytes(data[27:30], "little")
            return {"format": "webp", "width": width, "height": height}

    raise Exception("Format non reconnu ou non supporté")

def find_elements_by_local_name(root, path_parts):
    """Recherche des éléments en ignorant les namespaces"""
    results = []
    
    def get_local_name(tag):
        return tag.split('}')[-1] if '}' in tag else tag
    
    def search_recursive(element, remaining_path):
        if not remaining_path:
            results.append(element)
            return
        
        target = remaining_path[0]
        for child in element:
            if get_local_name(child.tag) == target:
                search_recursive(child, remaining_path[1:])
    
    for elem in root.iter():
        if get_local_name(elem.tag) == path_parts[0]:
            search_recursive(elem, path_parts[1:])
    
    return results

def get_valid_thumbnail_from_mtd(mtd_url, max_width, max_height, verbose=False):
    """
        Fonction pour obtenir une miniature valide
        On cherche une image avec largeur et hauteur <= 60px
        Retourne l'URL de la première image valide trouvée, ou une chaîne vide si aucune n'est trouvée
        Args:
            mtd_url (str): string URL d'une métadonnée  

        Returns:
            Boolean : True si une image valide est trouvée, False sinon
    """
    if (mtd_url and "csw?" in mtd_url):
        if verbose:
            print(f" --> Récupération des métadonnées depuis : {mtd_url} ")

        mtd_xml = getMetadata(mtd_url)
        root = ET.fromstring(mtd_xml)  # ou ET.fromstring(xml_string)
        
        # Recherche sans namespace
        path_parts = ["graphicOverview", "MD_BrowseGraphic", "fileName", "CharacterString"]
        url_elements = find_elements_by_local_name(root, path_parts)
        
        if not url_elements:
            if verbose:
                print(" --> Aucune miniature trouvée dans les métadonnées (XPath). ")
            return None
        
        for url_elem in url_elements:
            if url_elem.text:
                image = get_image_dimensions(url_elem.text)
                if image and image['width'] <= max_width and image['height'] <= max_height:
                    if verbose:
                        print(f" --> miniature valide (dimensions : {image['width']}x{image['height']}) : {url_elem.text} ")
                    return url_elem.text
                else:
                    if verbose:
                        print(f" --> miniature non valide (dimensions : {image['width']}x{image['height']}) : {url_elem.text} ")
                    return None
        if verbose:
            print(f" --> Aucune miniature valide trouvée dans les métadonnées depuis : {mtd_url} ")
    return None