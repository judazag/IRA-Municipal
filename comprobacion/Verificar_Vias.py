import osmnx as ox
import geopandas as gpd

lugar = "Salento, Quindío, Colombia"
G = ox.graph_from_place(lugar, network_type="all")
gdf_edges = ox.graph_to_gdfs(G, nodes=False)

print(f"✅ OSM funciona — {len(gdf_edges)} segmentos viales en {lugar}")

# Normalizar highway (puede ser string o lista)
gdf_edges["highway_clean"] = gdf_edges["highway"].apply(
    lambda x: x[0] if isinstance(x, list) else x
)
print(f"Tipos de vía: {gdf_edges['highway_clean'].value_counts().to_dict()}")

# Calcular longitud total en km
gdf_edges_proj = gdf_edges.to_crs(epsg=3116)  # Magna-Sirgas Colombia
total_km = gdf_edges_proj.geometry.length.sum() / 1000
print(f"Longitud total red vial: {total_km:.2f} km")