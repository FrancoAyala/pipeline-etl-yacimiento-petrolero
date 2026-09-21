from functools import wraps
import random

from flask import Flask, jsonify, request

app = Flask(__name__)

import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")


def requiere_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        clave_recibida = request.headers.get("X-API-Key")
        if clave_recibida != API_KEY:
            return jsonify({"error": "API key inválida o faltante"}), 401
        return func(*args, **kwargs)
    return wrapper


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/leases", methods=["GET"])
@requiere_api_key
def get_leases():
    leases = [
        {
            "lease_id": "LEASE-001",
            "lease_name": "Cactus Draw Block A",
            "geometry_wkt": "POLYGON((0 0, 1000 0, 1000 700, 700 700, 700 1000, 0 1000, 0 0))",
            "crs": "EPSG:32615",
        }
    ]
    return jsonify(leases)


@app.route("/wells", methods=["GET"])
@requiere_api_key
def get_wells():
    random.seed(7)
    statuses = ["producing", "drilling", "completed", "shut-in"]
    wells = []

    for i in range(1, 51):
        wells.append({
            "well_id": f"W-{i:03d}",
            "lease_id": "LEASE-001",
            "x": round(random.uniform(0, 1000), 2),
            "y": round(random.uniform(0, 1000), 2),
            "status": random.choice(statuses),
            "depth_m": round(random.uniform(1000, 4000), 1),
        })

    wells.append({"well_id": "W-005", "lease_id": "LEASE-001", "x": 999.0, "y": 999.0, "status": "producing", "depth_m": 2500.0})
    wells.append({"well_id": "W-999", "lease_id": "LEASE-001", "x": None, "y": None, "status": "drilling", "depth_m": 2500.0})
    wells.append({"well_id": "W-998", "lease_id": "LEASE-777", "x": 500.0, "y": 500.0, "status": "producing", "depth_m": 2500.0})

    return jsonify(wells)


if __name__ == "__main__":
    app.run(port=5000, debug=False)