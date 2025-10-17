import sys
import os

import unittest
import json
from core.entree_carto.thumbnail import get_valid_thumbnail_from_mtd

class TestThumbnail(unittest.TestCase):
    """
    Test la fusion du service de recherche avec la configuration issues des GetCapabilities
    """
    @classmethod
    def setUpClass(cls):
        # Charger les fichiers
        base_path = os.path.dirname(__file__)
        cls.url = "https://data.geopf.fr/csw?REQUEST=GetRecordById&SERVICE=CSW&VERSION=2.0.2&OUTPUTSCHEMA=http%3A%2F%2Fwww.isotc211.org%2F2005%2Fgmd&elementSetName=full&ID=adminexpress_departement-jpb" 
        # Appeler la fonction à tester
        cls.valid_thumbnail = get_valid_thumbnail_from_mtd(cls.url, 60, 60)

    def test_add_thumbnail(self):
        self.assertEqual(
            self.valid_thumbnail,
            "https://data.geopf.fr/annexes/cartes.gouv.fr-config/thumbnail/f6876c32-f294-43fc-bd20-00a5a66a1882.png"
        )

if __name__ == '__main__':
    unittest.main()
