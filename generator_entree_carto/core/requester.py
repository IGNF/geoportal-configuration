import requests
from functools import lru_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Session HTTP partagée : réutilise les connexions (keep-alive) au lieu d'en
# rouvrir une par requête. Sur data.geopf.fr (~7000 appels dans ce script),
# ça évite ~7000 handshakes TCP/TLS redondants.
DEFAULT_TIMEOUT = 15  # secondes ; évite qu'une requête traîne indéfiniment

_session = requests.Session()
_retries = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=frozenset(["HEAD", "GET", "POST"]),
)
# pool_maxsize doit couvrir le nombre de threads utilisés en parallèle
# (voir merger.py) sous peine de reconnexions.
_adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20, max_retries=_retries)
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)


def getEdito():
    url = "https://data.geopf.fr/annexes/cartes.gouv.fr-config/public/edito.json"
    response = _session.get(url, timeout=DEFAULT_TIMEOUT)
    if response.status_code != 200:
        return False
    return response.json()

@lru_cache(maxsize=4096)
def getMetadata(url):
    # Mise en cache : si plusieurs couches partagent la même URL de métadonnées
    # CSW, on ne la télécharge qu'une seule fois pour toute l'exécution.
    response = _session.get(url, timeout=DEFAULT_TIMEOUT)
    if response.status_code != 200:
        return False
    return response.content

def searchMtdUrls(layers_name, service, verbose=False):
    size = 100
    page = 1
    results = []
    url = "https://data.geopf.fr/recherche/api/indexes/geoplateforme"

    while True:
        # Paramètres de l'URL
        params = {
            'page': page,
            'size': size
        }

        # Corps de la requête
        #   "metadata_urls": True
        #   "aggregation" : {"fields": ["layer_name"]}"
        request_body = {
            "layer_name" : layers_name,
            "type" : service,
            "aggregation" : {"fields": ["layer_name"]}
        }

        response = _session.post(url, params=params, json=request_body, timeout=DEFAULT_TIMEOUT)
        if response.status_code != 200:
            return False

        data = response.json()

        # Vérifier si le tableau documents est vide
        if not data.get('documents') or len(data['documents']) == 0:
            break

        # Ajouter les résultats de cette page
        results.extend(data['documents'])

        if verbose:
            print(f"    --> page {page} : {len(data.get('documents', []))} résultats")

        # Passer à la page suivante
        page += 1
        # NB : le "return results" était auparavant ICI, dans la boucle,
        # ce qui empêchait de jamais récupérer une page 2. Corrigé : on
        # continue tant qu'il y a des résultats, et on retourne après la boucle.

    return results

def getHeadRequest(url, referer=""):
    response = _session.head(url, headers={'referer': referer}, timeout=DEFAULT_TIMEOUT)
    if response.status_code != 200:
        return False
    return response.headers