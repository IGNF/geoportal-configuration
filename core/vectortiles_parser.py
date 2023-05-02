import json

from pathlib import Path

def parseVectorTiles(key):
    filepath = Path("vectorTileConfig") / "{}VectorTileConfig.json".format(key)
    if not filepath.exists():
        return False
    with open(filepath, "r") as vector_tile_config_file:
        vector_tile_config = json.load(vector_tile_config_file)
    return vector_tile_config

if __name__ == "__main__":
    print(parseVectorTiles("essentiels"))
