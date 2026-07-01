import pandas as pd
from pipeline.ingesta.soda.conector_soda import ConectorSODA
from pipeline.utils.logger import get_logger

logger = get_logger("ingesta.eva")

DATASET_ID = "uejq-wxrr"
NOMBRE = "eva_2019_2023"
FUENTE = "eva"

COLUMNAS = [
    "c_digo_dane_departamento",
    "departamento",
    "c_digo_dane_municipio",
    "municipio",
    "grupo_cultivo",
    "subgrupo",
    "cultivo",
    "a_o",
    "rea_sembrada",
    "rea_cosechada",
    "producci_n",
    "rendimiento",
    "ciclo_del_cultivo",
]

def limpiar_eva(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Limpiando EVA...")

    # DIVIPOLA — asegurar 5 dígitos
    df["divipola"] = df["c_digo_dane_municipio"].astype(str).str.zfill(5)
    df["cod_depto"] = df["c_digo_dane_departamento"].astype(str).str.zfill(2)

    # Tipos numéricos
    for col in ["rea_sembrada", "rea_cosechada", "producci_n", "rendimiento"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Año como entero
    df["a_o"] = pd.to_numeric(df["a_o"], errors="coerce").astype("Int64")

    # Nombres limpios
    df = df.rename(columns={
        "c_digo_dane_municipio": "cod_municipio_raw",
        "c_digo_dane_departamento": "cod_depto_raw",
        "rea_sembrada": "area_sembrada_ha",
        "rea_cosechada": "area_cosechada_ha",
        "producci_n": "produccion_ton",
        "rendimiento": "rendimiento_ton_ha",
        "a_o": "anio",
    })

    # Eliminar registros sin DIVIPOLA válido
    df = df.dropna(subset=["divipola"])
    df = df[df["divipola"].str.len() == 5]

    logger.info(f"EVA limpia: {len(df):,} registros | {df['divipola'].nunique():,} municipios | {df['anio'].nunique()} años")
    return df

def ejecutar() -> pd.DataFrame:
    with ConectorSODA() as soda:
        df_raw = soda.descargar_y_guardar(
            dataset_id=DATASET_ID,
            nombre=NOMBRE,
            fuente=FUENTE,
            columnas=COLUMNAS,
        )

    df_limpio = limpiar_eva(df_raw)

    # Guardar versión limpia
    import pyarrow as pa
    import pyarrow.parquet as pq
    from pathlib import Path

    ruta = Path("data/raw/eva")
    ruta.mkdir(parents=True, exist_ok=True)
    archivo = ruta / "eva_limpia.parquet"
    pq.write_table(pa.Table.from_pandas(df_limpio), archivo, compression="snappy")
    logger.info(f"EVA limpia guardada: {archivo}")

    return df_limpio

if __name__ == "__main__":
    df = ejecutar()
    print(f"\nRegistros: {len(df):,}")
    print(f"Municipios únicos: {df['divipola'].nunique():,}")
    print(f"Años disponibles: {sorted(df['anio'].dropna().unique().tolist())}")
    print(f"Cultivos únicos: {df['cultivo'].nunique():,}")
    print(f"\nMuestra:")
    print(df[["divipola", "municipio", "cultivo", "anio", "produccion_ton", "rendimiento_ton_ha"]].head(5).to_string())
