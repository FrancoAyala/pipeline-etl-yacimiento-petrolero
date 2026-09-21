import json
import requests

import os
from dotenv import load_dotenv

load_dotenv()
headers = {"X-API-Key": os.getenv("API_KEY")}

respuesta_leases = requests.get("http://localhost:5000/leases", headers=headers)
respuesta_leases.raise_for_status()
leases = respuesta_leases.json()

respuesta_wells = requests.get("http://localhost:5000/wells", headers=headers)
respuesta_wells.raise_for_status()
wells = respuesta_wells.json()

print("Leases recibidos:", len(leases))
print("Wells recibidos:", len(wells))

payload = {"leases": leases, "wells": wells}

with open("data/raw/api_response.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

print("Guardado en data/raw/api_response.json")