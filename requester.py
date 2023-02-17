import requests
import xmltodict

def getWMTSCapabilities(key):
    url = "https://wxs.ign.fr/{}/geoportail/wmts?SERVICE=WMTS&REQUEST=GetCapabilities".format(key)
    response = requests.get(url)
    dict_capabilities = xmltodict.parse(response.text)

    return dict_capabilities["Capabilities"]

def getWMSRCapabilities(key):
    url = "https://wxs.ign.fr/{}/geoportail/r/wms?SERVICE=WMS&REQUEST=GetCapabilities".format(key)
    response = requests.get(url)
    dict_capabilities = xmltodict.parse(response.text)

    return dict_capabilities["Capabilities"]

def getWMSVCapabilities(key):
    url = "https://wxs.ign.fr/{}/geoportail/v/wms?SERVICE=WMS&REQUEST=GetCapabilities".format(key)
    response = requests.get(url)
    dict_capabilities = xmltodict.parse(response.text)

    return dict_capabilities["Capabilities"]
