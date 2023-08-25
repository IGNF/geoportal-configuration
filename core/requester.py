import requests
import xmltodict

def getWMTSCapabilities(key):
    url = "https://data.geopf.fr/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities"
    response = requests.get(url)
    if response.status_code != 200:
        return False
    dict_capabilities = xmltodict.parse(response.text)

    return dict_capabilities["Capabilities"]

def getWMSRCapabilities(key):
    url = "https://data.geopf.fr/wms-r/wms?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities"
    if key == "inspire":
        url = "https://wms-r.geopf.fr/rok4/wms?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities"
    response = requests.get(url)
    if response.status_code != 200:
        return False
    dict_capabilities = xmltodict.parse(response.text)

    return dict_capabilities["WMS_Capabilities"]["Capability"]

def getWMSVCapabilities(key):
    url = "https://data.geopf.fr/wms-v/ows?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities"
    if key == "inspire":
        url = "https://wms-v.geopf.fr/geoserver/ows?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities"
    response = requests.get(url)
    if response.status_code != 200:
        return False
    dict_capabilities = xmltodict.parse(response.text)

    return dict_capabilities["WMS_Capabilities"]["Capability"]
