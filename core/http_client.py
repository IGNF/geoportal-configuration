"""
Session HTTP partagée pour les appels à la Géoplateforme.

Une génération enchaîne plusieurs centaines de requêtes : sans nouvelle tentative,
une seule erreur réseau passagère (coupure, 502/503, timeout) faisait planter
main.py et échouer tout le workflow.

- nouvelles tentatives sur erreurs de connexion / lecture et sur 429, 500, 502, 503, 504
  (attente exponentielle : 0, 2, 4, 8, 16 s) ;
- timeout de connexion et de lecture (le timeout de lecture porte sur
  l'attente entre deux paquets, pas sur la durée totale du téléchargement) ;
- réutilisation des connexions (keep-alive), session utilisable depuis plusieurs threads.

Si le statut reste en erreur après les nouvelles tentatives, la réponse est renvoyée
telle quelle (raise_on_status=False) : l'appelant garde son comportement
habituel (status_code != 200 => service ignoré). Une erreur réseau persistante
lève toujours une exception.
"""
import os

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# (connexion, lecture) en secondes
DEFAULT_TIMEOUT = (10, 60)

# Parallélisation des requêtes (même principe que ENTREE_CARTO_MAX_WORKERS
# dans generator_entree_carto) : nombre de requêtes simultanées, réglable via
# la variable d'environnement CONFIG_MAX_WORKERS.
DEFAULT_MAX_WORKERS = 8
# Borne haute pour ne pas saturer data.geopf.fr ni le pool de connexions.
MAX_MAX_WORKERS = 20


def get_max_workers():
    raw = os.environ.get("CONFIG_MAX_WORKERS", str(DEFAULT_MAX_WORKERS))
    try:
        value = int(raw)
    except (TypeError, ValueError):
        value = DEFAULT_MAX_WORKERS
    return min(MAX_MAX_WORKERS, max(1, value))


_retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=frozenset(["HEAD", "GET"]),
    raise_on_status=False,
    respect_retry_after_header=True,
)
# pool_maxsize doit couvrir le nombre de threads utilisés en parallèle
# sous peine de reconnexions.
_adapter = HTTPAdapter(pool_connections=MAX_MAX_WORKERS, pool_maxsize=MAX_MAX_WORKERS, max_retries=_retries)

session = requests.Session()
session.mount("https://", _adapter)
session.mount("http://", _adapter)


def get(url, referer="", **kwargs):
    """GET avec nouvelles tentatives et timeout. Envoie l'en-tête Referer comme avant."""
    headers = kwargs.pop("headers", {}) or {}
    headers.setdefault("Referer", referer)
    kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
    return session.get(url, headers=headers, **kwargs)
