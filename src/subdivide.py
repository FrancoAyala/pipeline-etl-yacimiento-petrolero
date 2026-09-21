import sqlite3
import pandas as pd
from shapely import wkt

conexion = sqlite3.connect("db/pipeline.db")
leases_df = pd.read_sql("SELECT * FROM leases", conexion)
conexion.close()

lease_row = leases_df.iloc[0]
acreage = wkt.loads(lease_row["geometry_wkt"])

print("Lease cargado desde la DB:", lease_row["lease_name"])

print("Área del terreno:", acreage.area)
print("¿Es válido el polígono?", acreage.is_valid)


from shapely.geometry import box

ancho_dsu = 200
alto_dsu = 200

minx, miny, maxx, maxy = acreage.bounds
print("Límites del terreno (bounding box):", acreage.bounds)

celdas = []
x = minx
while x < maxx:
    y = miny
    while y < maxy:
        celda = box(x, y, x + ancho_dsu, y + alto_dsu)
        recortada = celda.intersection(acreage)
        if not recortada.is_empty and recortada.area > 0:
            celdas.append(recortada)
        y += alto_dsu
    x += ancho_dsu

print("Cantidad de DSUs generadas:", len(celdas))




from shapely.ops import unary_union

union_celdas = unary_union(celdas)

area_huecos = acreage.difference(union_celdas).area
area_huerfana = union_celdas.difference(acreage).area

print("Área de huecos:", area_huecos)
print("Área huérfana (fuera del terreno):", area_huerfana)

if area_huecos < 1e-6 and area_huerfana < 1e-6:
    print("La subdivisión es válida: sin huecos ni áreas huérfanas.")
else:
    print("Hay un problema en la subdivisión.")

from shapely.geometry import Point

conexion = sqlite3.connect("db/pipeline.db")
wells_df = pd.read_sql("SELECT * FROM wells", conexion)
conexion.close()

pozos = [Point(x, y) for x, y in zip(wells_df["x"], wells_df["y"])]
estados = wells_df["status"].tolist()
ids_pozos = wells_df["well_id"].tolist()

print("Pozos cargados desde la DB:", len(pozos))


import geopandas as gpd
import matplotlib.pyplot as plt

celdas_gdf = gpd.GeoDataFrame({"dsu_id": range(1, len(celdas) + 1)}, geometry=celdas, crs="EPSG:32615")
terreno_gdf = gpd.GeoDataFrame({"nombre": ["terreno"]}, geometry=[acreage], crs="EPSG:32615")

pozos_gdf = gpd.GeoDataFrame({"pozo_id": ids_pozos, "status": estados}, geometry=pozos, crs="EPSG:32615")

fig, ax = plt.subplots(figsize=(8, 8))
celdas_gdf.plot(ax=ax, facecolor="lightblue", edgecolor="blue", alpha=0.6)
terreno_gdf.boundary.plot(ax=ax, color="black", linewidth=2)
pozos_gdf.plot(ax=ax, color="red", markersize=60, edgecolor="black", zorder=5)
ax.set_title("Terreno subdividido en DSUs con pozos")
ax.set_aspect("equal")

plt.savefig("output/mapa.png")
print("Mapa guardado en output/mapa.png")


