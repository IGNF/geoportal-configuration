import json

def GENERIC_KEYS():
    with open("generic_keys.json", "r", newline='', encoding="utf-8") as file:
      GENERIC_KEYS = json.load(file)
    return GENERIC_KEYS