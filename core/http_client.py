"""
Session HTTP partagée pour les appels à la Géoplateforme.

Une génération enchaîne plusieurs centaines de requêtes : sans nouvelle tentative,
une seule erreur réseau passagère (coupure, 502/503, timeout) faisait planter
main.py et échouer tout le workflow.

- nouvelles tentatives sur erreurs de connexion / lecture et sur 429, 500, 502, 503, 504
  (attente exponentielle : 0, 2, 4, 8, 16 s) ;
- timeout de connexion et de lecture (le timeout de lecture porte sur
  l'attente entre deux paquets, pas sur la durée totale du téléchargement) ;
- réutilisation des connexions (keep-alive).

Si le statut reste en erreur après les nouvelles tentatives, la réponse est renvoyée
telle quelle (raise_on_status=False) : l'appelant garde son comportement
habituel (status_code != 200 => service ignoré). Une erreur réseau persistante
lève toujours une exception.
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# (connexion, lecture) en secondes
DEFAULT_TIMEOUT = (10, 60)

_retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=frozenset(["HEAD", "GET"]),
    raise_on_status=False,
    respect_retry_after_header=True,
)
_adapter = HTTPAdapter(max_retries=_retries)

session = requests.Session()
session.mount("https://", _adapter)
session.mount("http://", _adapter)


def get(url, referer="", **kwargs):
    """GET avec nouvelles tentatives et timeout. Envoie l'en-tête Referer comme avant."""
    headers = kwargs.pop("headers", {}) or {}
    headers.setdefault("Referer", referer)
    kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
    return session.get(url, headers=headers, **kwargs)
