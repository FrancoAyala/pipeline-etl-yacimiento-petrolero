import json
import sqlite3
import pandas as pd

with open("data/processed/leases.json", encoding="utf-8") as f:
    leases = json.load(f)

with open("data/processed/wells_valid.json", encoding="utf-8") as f:
    wells = json.load(f)

leases_df = pd.DataFrame(leases)
wells_df = pd.DataFrame(wells)

print(leases_df)
print(wells_df)



wells_df["status"] = wells_df["status"].str.strip().str.lower()

conexion = sqlite3.connect("db/pipeline.db")

leases_df.to_sql("leases", conexion, if_exists="replace", index=False)
wells_df.to_sql("wells", conexion, if_exists="replace", index=False)

conexion.close()

print("Datos guardados en db/pipeline.db")

conexion = sqlite3.connect("db/pipeline.db")

resultado = pd.read_sql("SELECT * FROM wells WHERE status = 'producing'", conexion)
print(resultado)

conteo = pd.read_sql("SELECT status, COUNT(*) as cantidad FROM wells GROUP BY status", conexion)
print(conteo)

conexion.close()