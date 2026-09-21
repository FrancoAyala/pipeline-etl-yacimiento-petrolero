import sqlite3
import pandas as pd
import plotly.graph_objects as go
from shapely import wkt

conexion = sqlite3.connect("db/pipeline.db")
wells_df = pd.read_sql("SELECT * FROM wells", conexion)
leases_df = pd.read_sql("SELECT * FROM leases", conexion)
conexion.close()

wells_df["z"] = -wells_df["depth_m"]

colores_por_status = {
    "producing": "#00e676",
    "drilling": "#ffab00",
    "completed": "#2979ff",
    "shut-in": "#9e9e9e",
}

fig = go.Figure()

# --- Contorno del terreno, dibujado en la superficie (z=0) ---
acreage = wkt.loads(leases_df.iloc[0]["geometry_wkt"])
borde_x, borde_y = acreage.exterior.xy
fig.add_trace(go.Scatter3d(
    x=list(borde_x),
    y=list(borde_y),
    z=[0] * len(borde_x),
    mode="lines",
    line=dict(color="white", width=3),
    name="Límite del terreno",
    showlegend=True,
))

# --- Pozos, cada uno como línea vertical con la punta marcada ---
for status, color in colores_por_status.items():
    subset = wells_df[wells_df["status"] == status]

    primera_de_este_status = True
    for _, pozo in subset.iterrows():
        fig.add_trace(go.Scatter3d(
            x=[pozo["x"], pozo["x"]],
            y=[pozo["y"], pozo["y"]],
            z=[0, pozo["z"]],
            mode="lines+markers",
            line=dict(color=color, width=3),
            marker=dict(size=[0, 6], color=color, symbol="circle"),
            name=status,
            legendgroup=status,
            showlegend=primera_de_este_status,
            text=pozo["well_id"],
            hovertemplate=f"<b>{pozo['well_id']}</b><br>Status: {status}<br>Profundidad: {pozo['depth_m']:.0f} m<extra></extra>",
        ))
        primera_de_este_status = False

fig.update_layout(
    template="plotly_dark",
    title="Pozos en 3D — trayectoria vertical sobre el terreno",
    scene=dict(
        xaxis_title="X",
        yaxis_title="Y",
        zaxis_title="Profundidad (m)",
        aspectmode="manual",
        aspectratio=dict(x=1, y=1, z=0.7),
    ),
    legend=dict(bgcolor="rgba(0,0,0,0.4)"),
)

fig.write_html("output/pozos_3d.html")
print("Gráfico 3D guardado en output/pozos_3d.html")