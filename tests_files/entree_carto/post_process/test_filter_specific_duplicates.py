import sys
import os
from .. import test_setup

# Ajoute le dossier parent (la racine du projet) au path Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import json
from generator_entree_carto.core.post_processes import filter_specific_duplicates

class TestRemoveDuplicate(unittest.TestCase):
    def test_entree_carto_custom_same_name(self):
        # import json from test file
        with open(os.path.join(os.path.dirname(__file__), "layers_duplicate_same_name.json"), "r", encoding="utf-8") as file:
            same_name_layers_input = json.load(file)
        with open(os.path.join(os.path.dirname(__file__), "layers_duplicate_same_name_result.json"), "r", encoding="utf-8") as file:
            same_name_layers_result = json.load(file)
        self.assertEqual(filter_specific_duplicates(same_name_layers_input), same_name_layers_result)
    
    def test_entree_carto_custom_suffixed_name(self):
        with open(os.path.join(os.path.dirname(__file__), "layers_duplicate_3services.json"), "r", encoding="utf-8") as file:
            services_layers_input = json.load(file)
        with open(os.path.join(os.path.dirname(__file__), "layers_duplicate_3services_result.json"), "r", encoding="utf-8") as file:
            services_layers_result = json.load(file)
        self.assertEqual(filter_specific_duplicates(services_layers_input), services_layers_result)

if __name__ == '__main__':
    unittest.main()