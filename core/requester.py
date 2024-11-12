import requests
import xmltodict
import xml.etree.ElementTree as ET
import os

from core.generic_keys import GENERIC_KEYS

def getWMTSCapabilities(key, referer=""):
    if key in GENERIC_KEYS :
        url = "https://data.geopf.fr/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities"
    else:
        url = "https://data.geopf.fr/private/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities&apikey={}".format(key)

    response = requests.get(url, headers={'Referer': referer})
    if response.status_code != 200:
        return False
    dict_capabilities = xmltodict.parse(response.text)

    return dict_capabilities["Capabilities"]

def getWMSRCapabilities(key, referer=""):
    if key in GENERIC_KEYS:
        url = "https://data.geopf.fr/wms-r/wms?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities"
    else:
        url = "https://data.geopf.fr/private/wms-r?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities&apikey={}".format(key)

    response = requests.get(url, headers={'referer': referer})
    if response.status_code != 200:
        return False
    dict_capabilities = xmltodict.parse(response.text)

    return dict_capabilities["WMS_Capabilities"]["Capability"]

def getWMSVCapabilities(key, referer=""):
    if key in GENERIC_KEYS :
        url = "https://data.geopf.fr/wms-v/ows?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities"
    else:
        url = "https://data.geopf.fr/private/wms-v/ows?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities&apikey={}".format(key)

    response = requests.get(url, headers={'referer': referer})
    if response.status_code != 200:
        return False
    dict_capabilities = xmltodict.parse(response.text)

    return dict_capabilities["WMS_Capabilities"]["Capability"]

def getWFSCapabilities(key, referer=""):
    if key in GENERIC_KEYS :
        url = "https://data.geopf.fr/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities"
    else:
        url = "https://data.geopf.fr/private/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities&apikey={}".format(key)

    response = requests.get(url, headers={'referer': referer})
    if response.status_code != 200:
        return False
    with open("originalCapa.xml", "w", encoding="utf-8") as file:
        file.writelines(response.text)
    namespaces = {}
    for _, node in ET.iterparse("originalCapa.xml", events=['start-ns']):
        if node[0] == 'wfs':
            continue
        namespaces[node[0]] = node[1]
    for ns in namespaces:
        ET.register_namespace(ns, namespaces[ns])
    capabilities = ET.parse("originalCapa.xml")
    os.remove("originalCapa.xml")

    return [capabilities, namespaces]
