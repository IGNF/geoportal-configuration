import sys
import os

# Ajouter la racine du projet au sys.path
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'generator_entree_carto'))
print(root_path)
if root_path not in sys.path:
    sys.path.insert(0, root_path)