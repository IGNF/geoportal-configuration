import requests
import xmltodict

from core.generic_keys import GENERIC_KEYS

def getWMTSCapabilities(key, referer):
    if key in GENERIC_KEYS :
        url = "https://data.geopf.fr/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities"
    else:
        url = "https://data.geopf.fr/private/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities&apikey={}".format(key)

    response = requests.get(url, headers={'Referer': referer})
    if response.status_code != 200:
        return False
    dict_capabilities = xmltodict.parse(response.text)

    return dict_capabilities["Capabilities"]

def getWMSRCapabilities(key, referer):
    if key in GENERIC_KEYS:
        url = "https://data.geopf.fr/wms-r/wms?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities"
    else:
        url = "https://data.geopf.fr/private/wms-r?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities&apikey={}".format(key)

    response = requests.get(url, headers={'referer': referer})
    if response.status_code != 200:
        return False
    dict_capabilities = xmltodict.parse(response.text)

    return dict_capabilities["WMS_Capabilities"]["Capability"]

def getWMSVCapabilities(key, referer):
    if key in GENERIC_KEYS :
        url = "https://data.geopf.fr/wms-v/ows?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities"
    else:
        url = "https://data.geopf.fr/private/wms-v/ows?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities&apikey={}".format(key)

    response = requests.get(url, headers={'referer': referer})
    if response.status_code != 200:
        return False
    dict_capabilities = xmltodict.parse(response.text)

    return dict_capabilities["WMS_Capabilities"]["Capability"]
