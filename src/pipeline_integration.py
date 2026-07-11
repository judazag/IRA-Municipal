"""
pipeline_integration.py
Módulo de integración geoespacial y construcción de tabla maestra.

Funciones:
- descargar_poligonos_municipales: Descarga polígonos DANE desde SODA
- cruzar_estaciones_municipios: Asigna DIVIPOLA a estaciones IDEAM
- cruzar_normales_municipios: Asigna DIVIPOLA a normales climatológicas
- calcular_densidad_vial: Descarga OSM y calcula km vía / km² por municipio
- construir_tabla_maestra: Integra todas las fuentes en municipio_features
"""

import time
import warnings
import pandas as pd
import geopandas as gpd
import osmnx as ox
import pyarrow as pa
import pyarrow.parquet as pq
import numpy as np
import sys
from pathlib import Path
from shapely.geometry import Point
from sodapy import Socrata


from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config
from src.logger import get_logger

warnings.filterwarnings('ignore')
logger = get_logger("pipeline_integration")

ROOT         = Path(__file__).parent.parent
INTERMEDIATE = ROOT / config.paths.intermediate
PRIMARY      = ROOT / config.paths.primary
PRIMARY.mkdir(parents=True, exist_ok=True)

# ─── POLÍGONOS MUNICIPALES ────────────────────────────────────────────────────

def descargar_poligonos_municipales() -> gpd.GeoDataFrame:
    """
    Descarga polígonos municipales MGN 2024 DANE.
    Shapefile: MGN_ADM_MPIO_GRAFICO — 1.122 municipios
    CRS: EPSG:4326 (WGS84)
    """
    ruta_cache = INTERMEDIATE / "poligonos_municipales.parquet"

    if ruta_cache.exists():
        logger.info("Cargando polígonos municipales desde cache...")
        return gpd.read_parquet(ruta_cache)

    import zipfile
    import io
    import requests

    tmp = MGN_CACHE
    shp = tmp / "MGN_ADM_MPIO_GRAFICO.shp"

    # Descargar solo si no existe
    if not shp.exists():
        logger.info("Descargando MGN 2024 DANE (91.5 MB)...")
        url = "https://geoportal.dane.gov.co/descargas/mgn_2024/MGN2024_MPIO_POLITICO.zip"
        r = requests.get(url, timeout=120)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        tmp.mkdir(parents=True, exist_ok=True)
        z.extractall(tmp)
        logger.info("Extracción completa")

    # Leer shapefile
    logger.info("Leyendo shapefile MGN 2024...")
    gdf = gpd.read_file(shp)
    logger.info(f"CRS original: {gdf.crs}")

    # Convertir a WGS84 si es necesario
    if gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs("EPSG:4326")

    # Estandarizar columnas
    gdf["divipola"]     = gdf["mpio_cdpmp"].astype(str).str.zfill(5)
    gdf["municipio"]    = gdf["mpio_cnmbr"]
    gdf["departamento"] = gdf["dpto_cnmbr"]

    # Mantener solo columnas relevantes
    gdf = gdf[["divipola","municipio","departamento","geometry"]]

    logger.info(f"Municipios: {len(gdf):,}")
    logger.info(f"Muestra: {gdf['divipola'].head(3).tolist()}")

    # Guardar cache
    gdf.to_parquet(ruta_cache)
    logger.info("Cache guardado: poligonos_municipales.parquet")
    return gdf

# ─── CRUCE GEOESPACIAL ESTACIONES IDEAM ───────────────────────────────────────

def cruzar_estaciones_municipios() -> pd.DataFrame:
    """
    Asigna DIVIPOLA a cada estación IDEAM por cruce de coordenadas
    con polígonos municipales DANE.
    """
    ruta_salida = INTERMEDIATE / "estaciones_ideam_con_divipola.parquet"
    if ruta_salida.exists():
        logger.info("Cargando estaciones con DIVIPOLA desde cache...")
        return pd.read_parquet(ruta_salida)

    logger.info("Cruzando estaciones IDEAM con polígonos municipales...")

    # Cargar datos
    df_est = pd.read_parquet(INTERMEDIATE / "estaciones_ideam_limpia.parquet")
    gdf_mpio = descargar_poligonos_municipales()

    # Convertir estaciones a GeoDataFrame
    gdf_est = gpd.GeoDataFrame(
        df_est,
        geometry=gpd.points_from_xy(df_est["longitud"], df_est["latitud"]),
        crs="EPSG:4326"
    )

    # Cruce espacial
    logger.info(f"Estaciones: {len(gdf_est):,} | Municipios: {len(gdf_mpio):,}")
    gdf_join = gpd.sjoin(gdf_est, gdf_mpio[["divipola","municipio","departamento","geometry"]],
                         how="left", predicate="within")

    # Estadísticas
    con_divipola = gdf_join["divipola"].notna().sum()
    sin_divipola = gdf_join["divipola"].isna().sum()
    logger.info(f"Con DIVIPOLA: {con_divipola:,} | Sin DIVIPOLA: {sin_divipola:,}")

    df_resultado = pd.DataFrame(gdf_join.drop(columns=["geometry","index_right"]))

    pq.write_table(pa.Table.from_pandas(df_resultado), ruta_salida, compression="snappy")
    logger.info(f"Guardado: estaciones_ideam_con_divipola.parquet")
    return df_resultado

# ─── CRUCE NORMALES CLIMATOLÓGICAS ────────────────────────────────────────────

def cruzar_normales_municipios() -> pd.DataFrame:
    """
    Asigna DIVIPOLA a normales climatológicas via cruce con estaciones IDEAM.
    Usa periodo 1991-2020 como baseline.
    """
    ruta_salida = INTERMEDIATE / "normales_con_divipola.parquet"
    if ruta_salida.exists():
        logger.info("Cargando normales con DIVIPOLA desde cache...")
        return pd.read_parquet(ruta_salida)

    logger.info("Cruzando normales climatológicas con municipios...")

    df_norm = pd.read_parquet(INTERMEDIATE / "normales_climatologicas_limpia.parquet")
    df_est  = cruzar_estaciones_municipios()

    # Filtrar período 1991-2020
    df_norm_periodo = df_norm[df_norm["periodo"] == "1991-2020"].copy()
    logger.info(f"Normales 1991-2020: {len(df_norm_periodo):,} registros")

    # Cruce por código de estación
    df_est_div = df_est[["codigo","divipola"]].dropna(subset=["divipola"])
    df_resultado = df_norm_periodo.merge(df_est_div, left_on="codigo_estacion",
                                          right_on="codigo", how="left")

    con_div = df_resultado["divipola"].notna().sum()
    sin_div = df_resultado["divipola"].isna().sum()
    logger.info(f"Con DIVIPOLA: {con_div:,} | Sin DIVIPOLA: {sin_div:,}")

    pq.write_table(pa.Table.from_pandas(df_resultado), ruta_salida, compression="snappy")
    logger.info("Guardado: normales_con_divipola.parquet")
    return df_resultado

# ─── RED VIAL OSM ─────────────────────────────────────────────────────────────

def calcular_densidad_vial(
    muestra_municipios: list = None,
    tipos_via: list = None
) -> pd.DataFrame:
    """
    Descarga red vial de OpenStreetMap por municipio y calcula
    densidad vial rural (km vía / km² área municipal).

    Args:
        muestra_municipios: Lista de DIVIPOLA para prueba (None = todos)
        tipos_via: Tipos de vía a incluir (None = default rural)

    Returns:
        DataFrame con divipola y densidad_vial_km_km2
    """
    ruta_salida = INTERMEDIATE / "densidad_vial_osm.parquet"
    if ruta_salida.exists():
        logger.info("Cargando densidad vial desde cache...")
        return pd.read_parquet(ruta_salida)

    if tipos_via is None:
        tipos_via = ["secondary","tertiary","unclassified","residential","track"]

    logger.info("Calculando densidad vial rural por municipio (OSM)...")
    gdf_mpio = descargar_poligonos_municipales()

    if muestra_municipios:
        gdf_mpio = gdf_mpio[gdf_mpio["divipola"].isin(muestra_municipios)]
        logger.info(f"Procesando muestra: {len(gdf_mpio):,} municipios")
    else:
        logger.info(f"Procesando todos los municipios: {len(gdf_mpio):,}")

    resultados = []
    errores = 0

    for idx, row in gdf_mpio.iterrows():
        divipola = row.get("divipola", "")
        municipio = row.get("municipio", "")

        try:
            # Área municipal en km²
            gdf_proj = gpd.GeoDataFrame([row], geometry="geometry", crs="EPSG:4326")
            gdf_proj = gdf_proj.to_crs("EPSG:3116")  # Colombia Bogotá
            area_km2 = gdf_proj.geometry.area.iloc[0] / 1e6

            # Descargar red vial
            polygon = row["geometry"]
            G = ox.graph_from_polygon(
                polygon,
                network_type="drive",
                custom_filter=f'["highway"~"{"| ".join(tipos_via)}"]'
            )

            # Calcular longitud total en km
            edges = ox.graph_to_gdfs(G, nodes=False)
            edges_proj = edges.to_crs("EPSG:3116")
            longitud_km = edges_proj.geometry.length.sum() / 1000

            densidad = longitud_km / area_km2 if area_km2 > 0 else 0

            resultados.append({
                "divipola":           divipola,
                "municipio":          municipio,
                "area_km2":           round(area_km2, 2),
                "longitud_vial_km":   round(longitud_km, 2),
                "densidad_vial_km_km2": round(densidad, 4),
            })

            if len(resultados) % 50 == 0:
                logger.info(f"  Procesados: {len(resultados):,}/{len(gdf_mpio):,}")

        except Exception as e:
            logger.warning(f"  Sin red vial: {municipio} ({divipola}) — {e}")
            resultados.append({
                "divipola":             divipola,
                "municipio":            municipio,
                "area_km2":             0,
                "longitud_vial_km":     0,
                "densidad_vial_km_km2": 0,
            })
            errores += 1

        time.sleep(0.5)  # Rate limiting OSM

    df_resultado = pd.DataFrame(resultados)
    pq.write_table(pa.Table.from_pandas(df_resultado), ruta_salida, compression="snappy")

    logger.info(f"Densidad vial calculada: {len(df_resultado):,} municipios | {errores:,} sin red vial")
    logger.info(f"Promedio densidad: {df_resultado['densidad_vial_km_km2'].mean():.4f} km/km²")
    return df_resultado