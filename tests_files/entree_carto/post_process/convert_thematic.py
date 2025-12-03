import sys
import os
from .. import test_setup

import unittest
import json
from generator_entree_carto.core.merger import merge_edito
from generator_entree_carto.core.post_processes import convert_thematic

class TestThematicAndProducer(unittest.TestCase):
    """
    Test l'ajout des thématiques et producteurs depuis l'édito
    """
    @classmethod
    def setUpClass(cls):
        # Charger les fichiers
        base_path = os.path.dirname(__file__)
        with open(os.path.join(base_path, "2_search_service_merged.json"), "r", encoding="utf-8") as file:
            cls.merged_config = json.load(file)
        with open(os.path.join(base_path, "../edito.json"), "r", encoding="utf-8") as file:
            cls.edito = json.load(file)
        cls.converted = convert_thematic(cls.merged_config["layers"], cls.edito["topics"]["thematic"])

    def test_thematic_is_not_converted(self):
        self.assertEqual(
            "INRAthemeFromSearch" in self.converted["INRA.CARTE.SOLS$GEOPORTAIL:OGC:WMTS"]["thematic"],
            True)
    def test_thematic_is_converted(self):
        self.assertEqual(
            "Eaux intérieures, Hydrographie" in self.converted["hydro_ardennes_pyramide_raster_wmts$GEOPORTAIL:OGC:WMTS"]["thematic"],
            True)

if __name__ == '__main__':
    unittest.main()
