import requests

def getEdito():
    url = "https://data.geopf.fr/annexes/cartes.gouv.fr-config/public/edito.json"
    response = requests.get(url)
    if response.status_code != 200:
        return False
    return response.json()

def getMetadata(url):
    response = requests.get(url)
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
        
        response = requests.post(url, params=params, json=request_body)
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
        
        return results

def getHeadRequest(url, referer=""):
    response = requests.head(url, headers={'referer': referer})
    if response.status_code != 200:
        return False
    return response.headers