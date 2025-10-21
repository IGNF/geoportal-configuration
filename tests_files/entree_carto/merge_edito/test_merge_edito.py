import sys
import os

import unittest
import json
from core.entree_carto.merger import merge_edito
from core.requester import getEdito

class TestMergeServiceDeRecherche(unittest.TestCase):
    """
    Test la fusion du service de recherche avec la configuration issues des GetCapabilities
    """
    @classmethod
    def setUpClass(cls):
        # Charger les fichiers
        base_path = os.path.dirname(__file__)
        with open(os.path.join(base_path, "2_search_service_merged.json"), "r", encoding="utf-8") as file:
            cls.merged_config = json.load(file)
        with open(os.path.join(base_path, "edito.json"), "r", encoding="utf-8") as file:
            cls.edito = json.load(file)
        # Appeler la fonction à tester
        cls.edito_merged = merge_edito(cls.edito, cls.merged_config)
        with open(os.path.join(base_path, "edito_merged.json"), "w", encoding="utf-8") as file:
            file.writelines(json.dumps(cls.edito_merged, indent=2, ensure_ascii=False))

    def test_append_new_thematic(self):
        self.assertEqual(len(self.edito_merged["layers"]["INRA.CARTE.SOLS$GEOPORTAIL:OGC:WMTS"]["thematic"]), 1)
    def test_add_new_producer(self):
        self.assertEqual(self.edito_merged["layers"]["INRA.CARTE.SOLS$GEOPORTAIL:OGC:WMTS"]["producer"][0], "INRA")
    def test_no_duplicate_thematic(self):
        self.assertEqual(len(self.edito_merged["layers"]["hydro_ardennes_pyramide_raster_wmts$GEOPORTAIL:OGC:WMTS"]["thematic"]), 3)

    def test_merge_getcap_searchservice_thematic(self):
        self.assertIn(
            "NEWinlandWaters",
            self.edito_merged["layers"]["hydro_ardennes_pyramide_raster_wmts$GEOPORTAIL:OGC:WMTS"]["thematic"]
        )
    
    def test_has_base_key(self):
        self.assertEqual("base" in self.edito_merged["layers"]["hydro_ardennes_pyramide_raster_wmts$GEOPORTAIL:OGC:WMTS"], True)

    def test_add_other_edito_key(self):
        self.assertEqual("thematics" in self.edito_merged, True)
    
    def test_keep_same_layers_count(self):
        self.assertEqual(len(self.edito_merged["layers"]), len(self.merged_config["layers"]))
    
    def test_edito_delete_thematic(self):
        self.assertEqual(len(self.edito_merged["layers"]["PLAN.IGN$GEOPORTAIL:GPP:TMS"]["thematic"]), 0)

if __name__ == '__main__':
    unittest.main()
