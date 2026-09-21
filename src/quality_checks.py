import json

with open("data/raw/api_response.json", encoding="utf-8") as f:
    payload = json.load(f)

leases = payload["leases"]
wells = payload["wells"]

lease_ids_validos = {lease["lease_id"] for lease in leases}
print("Leases válidos:", lease_ids_validos)

campos_obligatorios = ["well_id", "lease_id", "x", "y"]
rango_valido_x = (0, 1000)
rango_valido_y = (0, 1000)

wells_validos = []
wells_rechazados = []
well_ids_vistos = set()

for well in wells:
    motivos = []

    for campo in campos_obligatorios:
        if well.get(campo) is None:
            motivos.append(f"campo obligatorio faltante: '{campo}'")

    if well.get("well_id") in well_ids_vistos:
        motivos.append(f"well_id duplicado: '{well['well_id']}'")

    if well.get("x") is not None and well.get("y") is not None:
        x, y = well["x"], well["y"]
        if not (rango_valido_x[0] <= x <= rango_valido_x[1]):
            motivos.append(f"coordenada X fuera de rango: {x}")
        if not (rango_valido_y[0] <= y <= rango_valido_y[1]):
            motivos.append(f"coordenada Y fuera de rango: {y}")

    if well.get("lease_id") not in lease_ids_validos:
        motivos.append(f"lease_id inexistente: '{well.get('lease_id')}' (well huérfano)")

    if motivos:
        well["motivos_rechazo"] = motivos
        wells_rechazados.append(well)
    else:
        wells_validos.append(well)
        well_ids_vistos.add(well["well_id"])

print("Válidos:", len(wells_validos))
print("Rechazados:", len(wells_rechazados))
for w in wells_rechazados:
    print(" -", w["well_id"], ":", w["motivos_rechazo"])


with open("data/processed/wells_valid.json", "w", encoding="utf-8") as f:
    json.dump(wells_validos, f, indent=2)

with open("data/processed/wells_rejected.json", "w", encoding="utf-8") as f:
    json.dump(wells_rechazados, f, indent=2)

with open("data/processed/leases.json", "w", encoding="utf-8") as f:
    json.dump(leases, f, indent=2)

print("Guardado en data/processed/")