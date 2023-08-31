import csv

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

