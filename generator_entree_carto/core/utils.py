import math

def get_max_tilematrix(max_scale_denominator: float, crs: str = "EPSG:3857", tile_size: int = 256) -> int:
    """
    Calcule le maxTileMatrix pour un TileMatrixSet à partir du maxScaleDenominator.

    :param max_scale_denominator: échelle maximale (ex: 5000 pour 1:5000)
    :param crs: 'EPSG:3857' ou 'EPSG:4326'
    :param tile_size: taille des tiles en pixels (par défaut 256)
    :return: niveau maximal de TileMatrix
    """
    # Constante DPI OGC (pixels par pouce)
    dpi = 25.4 / 0.28  # 90.7142857
    
    # Résolution du niveau 0
    if crs == "EPSG:3857":
        R = 6378137  # rayon du Mercator en mètres
        resolution_0 = 2 * math.pi * R / tile_size
    elif crs == "EPSG:4326":
        resolution_0 = 360 / tile_size
    else:
        print(f"CRS {crs} non supporté pour le calcul du maxTileMatrix.")
        return 0
    
    # Résolution minimale correspondant au maxScaleDenominator
    resolution_min = max_scale_denominator * 0.00028  # 0.28 mm par pixel
    
    # Calcul du niveau de TileMatrix max
    if resolution_min == 0:
        return 0
    max_tilematrix = round(math.log2(resolution_0 / resolution_min))
    return max_tilematrix


# Exemple d'utilisation
max_scale = 34123.673341596535  # 1:5000
crs = "EPSG:3857"
max_tile = get_max_tilematrix(max_scale, crs)
print(f"Max TileMatrix pour {crs} et maxScaleDenominator {max_scale} : {max_tile}")