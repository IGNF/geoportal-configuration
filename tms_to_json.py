import json
import os
import xmltodict

directory = 'TMS'

output = {}

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    output[os.path.splitext(filename)[0]] = []

    with open(f, "r") as file:
        dict_TMS = xmltodict.parse(file.read())
        for tilematrix in dict_TMS["tileMatrixSet"]["tileMatrix"]:
            output[os.path.splitext(filename)[0]].append(tilematrix["resolution"])

with open("nativeResolutions.json", "w", encoding="utf-8") as file:
    file.writelines(json.dumps(output, indent=2, ensure_ascii=False))
