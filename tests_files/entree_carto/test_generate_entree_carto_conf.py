import sys
import os
import test_setup

import unittest
import json
from generator_entree_carto.entree_carto import GenerateEntreeCarto

class TestGenerateEntreeCartoConf(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Charger les fichiers
        base_path = os.path.dirname(__file__)
        # with open(os.path.join(base_path, "1_merged_config_4layers.json"), "r", encoding="utf-8") as file:
        #     cls.merged_config = json.load(file)
        
        # cls.entree_carto_config = generate_entree_carto_conf(cls.merged_config)
        
        generator = GenerateEntreeCarto(
            input_path=os.path.join(base_path, "1_merged_config_4layers.json"),
            output_path=os.path.join(base_path, "entree_carto_config.json"),
            count="10",
        )
        cls.entree_carto_config = generator.run(verbose=False)

        # with open(os.path.join(base_path, "entree_carto_config.json"), "w", encoding="utf-8") as file:
        #     file.writelines(json.dumps(cls.entree_carto_config, indent=2, ensure_ascii=False))

    def test_add_layers(self):
        self.assertEqual(len(self.entree_carto_config["layers"]),4)

    def test_has_territories(self):
        self.assertEqual("territories" in self.entree_carto_config, True)

    def test_merged_plan_ign_thematic(self):
        self.assertEqual(len(self.entree_carto_config["layers"]["PLAN.IGN$GEOPORTAIL:GPP:TMS"]["thematic"]), 1)

if __name__ == '__main__':
    unittest.main()