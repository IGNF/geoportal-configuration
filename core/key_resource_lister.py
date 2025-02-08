import csv
import requests
import json

TMS_CONFIG = [
  {"service": "TMS", "key": "administratif", "layer": "ADMIN_EXPRESS"},
  {"service": "TMS", "key": "altimetrie", "layer": "ISOHYPSE"},
  {"service": "TMS", "key": "cartes", "layer": "PLAN.IGN"},
  {"service": "TMS", "key": "essentiels", "layer": "ADMIN_EXPRESS"},
  {"service": "TMS", "key": "essentiels", "layer": "PLAN.IGN"},
  {"service": "TMS", "key": "ocsge", "layer": "OCSGE_2016"},
  {"service": "TMS", "key": "ocsge", "layer": "OCSGE_2019"},
  {"service": "TMS", "key": "parcellaire", "layer": "PCI"},
  {"service": "TMS", "key": "topographie", "layer": "BDTOPO"}
]

def createKeyServiceLayersFile(
  url="https://data.geopf.fr/annexes/ressources/capabilities/services.csv",
  filePath="resources_by_key.csv"):
  with requests.Session() as s:
    download = s.get(url)
    decoded_content = download.content.decode("latin1")
    reader = csv.DictReader(decoded_content.splitlines(), delimiter=";")
  generic_keys = []
  with open(filePath, "w", newline='', encoding="utf-8") as csvFile:
    fieldnames = ["service", "key", "layer"]
    writer = csv.DictWriter(csvFile, fieldnames=fieldnames, lineterminator='\n')
    writer.writeheader()
    for newRow in TMS_CONFIG:
      writer.writerow(newRow)
    for row in reader:
      if row["Service"] == "WMTS":
        service = "WMTS"
      elif row["Service"] == "WMS Raster":
        service = "WMS"
      elif row["Service"] == "WMS Vecteur":
        service = "WMS"
      elif row["Service"] == "WFS":
        service = "WFS"
      else:
        continue

      if row["Thématique"] == "cle specifique *":
        continue
      if row["Thématique"] == "":
        continue
      generic_keys.append(row["Thématique"])
      newRow = {
        "service": service,
        "key": row["Thématique"],
        "layer": row["Nom technique"].strip()
      }
      writer.writerow(newRow)
    with open("generic_keys.json", "w", newline='', encoding="utf-8") as generic_keys_file:
      json.dump(list(set(generic_keys)), generic_keys_file)

def keysServicesLayers(filePath="resources_by_key.csv"):
  rows = []
  keys = []
  with open(filePath) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=",")
    for row in reader:
      rows.append(row)
      if row["key"] not in keys:
        keys.append(row["key"])

  keys_services_layers = {}
  for key in keys:
    keys_services_layers[key] = {}

    for row in rows:
      if row["key"] != key:
        continue
      if row["service"] not in keys_services_layers[key]:
        keys_services_layers[key][row["service"]] = []
      keys_services_layers[key][row["service"]].append(row["layer"])

  return keys_services_layers

