import sys
import os
from .. import test_setup

import unittest
import json
from generator_entree_carto.core.merger import merge_service_de_recherche_infos
from generator_entree_carto.core.requester import searchMtdUrls

class TestMergeServiceDeRecherche(unittest.TestCase):
    """
    Test la fusion du service de recherche avec la configuration issues des GetCapabilities
    """
    @classmethod
    def setUpClass(cls):
        # Charger les fichiers
        base_path = os.path.dirname(__file__)
        with open(os.path.join(base_path, "1_merged_config_5layers.json"), "r", encoding="utf-8") as file:
            cls.merged_config = json.load(file)
        with open(os.path.join(base_path, "service_recherche_with_metadata_urls.json"), "r", encoding="utf-8") as file:
            cls.search_result = json.load(file)
        with open(os.path.join(base_path, "2_search_service_merged.json"), "r", encoding="utf-8") as file:
            cls.excepted_search_merged = json.load(file)
        
        # Appeler la fonction à tester
        cls.search_merged = merge_service_de_recherche_infos(cls.search_result, cls.merged_config)

    def test_add_thematic_from_searchservice(self):
        self.assertEqual(
            len(self.search_merged["layers"]["INRA.CARTE.SOLS$GEOPORTAIL:OGC:WMTS"]["thematic"]),
            len(self.excepted_search_merged["layers"]["INRA.CARTE.SOLS$GEOPORTAIL:OGC:WMTS"]["thematic"])
        )

    def test_no_duplicate_thematic(self):
        self.assertEqual(
            len(self.search_merged["layers"]["hydro_ardennes_pyramide_raster_wmts$GEOPORTAIL:OGC:WMTS"]["thematic"]),
            len(self.excepted_search_merged["layers"]["hydro_ardennes_pyramide_raster_wmts$GEOPORTAIL:OGC:WMTS"]["thematic"])
        )

    def test_merge_getcap_searchservice_thematic(self):
        self.assertIn(
            "NEWinlandWaters",
            self.search_merged["layers"]["hydro_ardennes_pyramide_raster_wmts$GEOPORTAIL:OGC:WMTS"]["thematic"]
        )

    # AJOUTER RESULTET SERVICE DE RECHERCHE AVEC THUMBNAIL
    def test_thumbanil_is_valid(self):
        self.assertEqual(
            self.search_merged["layers"]["adminexpress-kdep-jpb-test-raster_wmts$GEOPORTAIL:OGC:WMTS"]["thumbnail"],
            self.excepted_search_merged["layers"]["adminexpress-kdep-jpb-test-raster_wmts$GEOPORTAIL:OGC:WMTS"]["thumbnail"]
        )

if __name__ == '__main__':
    unittest.main()
