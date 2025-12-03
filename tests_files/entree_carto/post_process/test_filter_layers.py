import sys
import os
from .. import test_setup

import unittest
import json
from generator_entree_carto.core.post_processes import filter_layers

class TestMergeServiceDeRecherche(unittest.TestCase):
    """
    Test la fusion du service de recherche avec la configuration issues des GetCapabilities
    """
    @classmethod
    def setUpClass(cls):
        # Charger les fichiers
        base_path = os.path.dirname(__file__)
        with open(os.path.join(base_path, "edito_merged_post_process.json"), "r", encoding="utf-8") as file:
            cls.config = json.load(file)
        # Appeler la fonction à tester
        cls.filtered_config = filter_layers(cls.config["layers"])

    def test_remove_service_param(self):
        self.assertEqual(len(self.filtered_config), 3)

if __name__ == '__main__':
    unittest.main()
