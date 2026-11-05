import requests
import xmltodict
import xml.etree.ElementTree as ET
import os
import time
from xml.parsers.expat import ExpatError

from core.generic_keys import GENERIC_KEYS

# (connect, read) en secondes : le GetCapabilities WFS (~5 Mo) peut mettre plus d'une minute à répondre
REQUEST_TIMEOUT = (30, 120)
MAX_ATTEMPTS = 3
RETRY_DELAY = 5


class CapabilitiesUnavailable(Exception):
    """Service injoignable (erreur réseau, timeout, 429 ou 5xx) malgré les retries.
    La config de la clé ne doit pas être générée : elle serait incomplète."""


def _get(url, referer, service_name, key):
    """GET avec timeout et retries sur erreur réseau / 429 / 5xx.
    Renvoie la réponse HTTP 200, None sur une autre erreur HTTP (4xx : service
    non disponible pour cette clé), et lève CapabilitiesUnavailable si le
    service reste injoignable après MAX_ATTEMPTS tentatives."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(url, headers={'Referer': referer}, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                return response
            reason = "HTTP {}".format(response.status_code)
            if response.status_code != 429 and response.status_code < 500:
                print("Skipping {} capabilities for key '{}': {}".format(service_name, key, reason))
                return None
        except requests.RequestException as error:
            reason = "{}: {}".format(type(error).__name__, error)
        if attempt < MAX_ATTEMPTS:
            print("{} capabilities for key '{}' failed ({}), retry {}/{}".format(service_name, key, reason, attempt, MAX_ATTEMPTS - 1))
            time.sleep(RETRY_DELAY * attempt)
    raise CapabilitiesUnavailable("{} capabilities for key '{}' unavailable after {} attempts ({})".format(service_name, key, MAX_ATTEMPTS, reason))


def _parse_xmltodict_response(response_text, service_name, key):
    try:
        return xmltodict.parse(response_text)
    except ExpatError as error:
        print("Skipping {} capabilities for key '{}': malformed XML ({})".format(service_name, key, error))
        return False



def getWMTSCapabilities(key, referer=""):
    if key in GENERIC_KEYS() :
        url = "https://data.geopf.fr/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities"
    else:
        url = "https://data.geopf.fr/private/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities&apikey={}".format(key)

    response = _get(url, referer, "WMTS", key)
    if response is None:
        return False
    dict_capabilities = _parse_xmltodict_response(response.text, "WMTS", key)
    if dict_capabilities == False:
        return False

    return dict_capabilities["Capabilities"]

def getWMSRCapabilities(key, referer=""):
    if key in GENERIC_KEYS() :
        url = "https://data.geopf.fr/wms-r/wms?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities"
    else:
        url = "https://data.geopf.fr/private/wms-r?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities&apikey={}".format(key)

    response = _get(url, referer, "WMS-R", key)
    if response is None:
        return False
    dict_capabilities = _parse_xmltodict_response(response.text, "WMS-R", key)
    if dict_capabilities == False:
        return False

    return dict_capabilities["WMS_Capabilities"]["Capability"]

def getWMSVCapabilities(key, referer=""):
    if key in GENERIC_KEYS() :
        url = "https://data.geopf.fr/wms-v/ows?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities"
    else:
        url = "https://data.geopf.fr/private/wms-v/ows?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities&apikey={}".format(key)

    response = _get(url, referer, "WMS-V", key)
    if response is None:
        return False
    dict_capabilities = _parse_xmltodict_response(response.text, "WMS-V", key)
    if dict_capabilities == False:
        return False

    return dict_capabilities["WMS_Capabilities"]["Capability"]

def getWFSCapabilities(key, referer=""):
    if key in GENERIC_KEYS() :
        url = "https://data.geopf.fr/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities"
    else:
        url = "https://data.geopf.fr/private/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities&apikey={}".format(key)

    response = _get(url, referer, "WFS", key)
    if response is None:
        return [False, False]
    with open("originalCapa.xml", "w", encoding="utf-8") as file:
        file.writelines(response.text)
    try:
        namespaces = {}
        for _, node in ET.iterparse("originalCapa.xml", events=['start-ns']):
            if node[0] == 'wfs':
                continue
            namespaces[node[0]] = node[1]
        for ns in namespaces:
            ET.register_namespace(ns, namespaces[ns])
        capabilities = ET.parse("originalCapa.xml")
    except ET.ParseError as error:
        print("Skipping WFS capabilities for key '{}': malformed XML ({})".format(key, error))
        return [False, False]
    finally:
        if os.path.exists("originalCapa.xml"):
            os.remove("originalCapa.xml")

    return [capabilities, namespaces]

def getTMSTileMaps(key, referer=""):
    if key in GENERIC_KEYS() :
        url = "https://data.geopf.fr/tms/1.0.0"
    else:
        return {}

    response = _get(url, referer, "TMS", key)
    if response is None:
        return False
    dict_capabilities = _parse_xmltodict_response(response.text, "TMS", key)
    if dict_capabilities == False:
        return False

    return dict_capabilities["TileMapService"]["TileMaps"]["TileMap"]
