import pandas as pd
import requests
import io
import os

# ─── Victimas ECV corregido ───────────────────────────────────────────────────
print("=" * 60)
print("Victimas ECV — separador corregido")
print("=" * 60)
try:
    df = pd.read_csv("csv/FEX_VICTIMA_ECV_2024.csv", sep=";")
    print(f"Filas: {len(df)} | Columnas: {len(df.columns)}")
    print(f"Columnas: {list(df.columns)}")
    print(f"\nMuestra fila 1:")
    for col, val in df.iloc[0].items():
        print(f"  {col}: {val}")
except Exception as e:
    print(f"ERROR: {e}")

# ─── SIPSA-A ──────────────────────────────────────────────────────────────────
print("=" * 60)
print("SIPSA-A")
print("=" * 60)
try:
    df_a = pd.read_csv(
        "comprobacion/csv/2026 (I cuatrimestre).csv",
        sep=";",
        encoding="latin-1",
        dtype=str  # todo como string para no perder el apóstrofe
    )
    print(f"Filas: {len(df_a)} | Columnas: {len(df_a.columns)}")
    print(f"Columnas: {list(df_a.columns)}")
    print(f"\nMuestra fila 1:")
    for col, val in df_a.iloc[0].items():
        print(f"  {col}: {val}")

    # Limpiar apóstrofe del DIVIPOLA
    col_divipola = "Divipola Municipio / ISO 3166-1 País Proc."
    df_a["divipola"] = df_a[col_divipola].str.replace("'", "").str.zfill(5)
    print(f"\nMunicipios únicos origen: {df_a['divipola'].nunique()}")
    print(f"Muestra DIVIPOLA: {df_a['divipola'].head(5).tolist()}")

    # Grupos de alimentos disponibles
    print(f"\nGrupos únicos: {df_a['Grupo'].unique().tolist()}")
except Exception as e:
    print(f"ERROR SIPSA-A: {e}")

# ─── SIPSA-P ──────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SIPSA-P")
print("=" * 60)
try:
    df_p = pd.read_csv(
        "csv/mensual 24.csv",
        sep=";",
        encoding="utf-8-sig"  # maneja el BOM automáticamente
    )
    print(f"Filas: {len(df_p)} | Columnas: {len(df_p.columns)}")
    print(f"Columnas: {list(df_p.columns)}")
    print(f"\nMuestra fila 1:")
    for col, val in df_p.iloc[0].items():
        print(f"  {col}: {val}")

    # Mercados únicos
    print(f"\nMercados únicos: {df_p['Mercado'].nunique()}")
    print(f"Muestra mercados: {df_p['Mercado'].unique()[:5].tolist()}")

    # Grupos disponibles
    print(f"\nGrupos únicos: {df_p['Grupo'].unique().tolist()}")
except Exception as e:
    print(f"ERROR SIPSA-P: {e}")

# ─── NOAA ONI ─────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("NOAA ONI")
print("=" * 60)
try:
    url = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
    r = requests.get(url, timeout=15)
    lineas = r.text.strip().split("\n")
    print(f"Total registros: {len(lineas)}")
    print(f"Encabezado:   {lineas[0]}")
    print(f"Primera fila: {lineas[1]}")
    print(f"Última fila:  {lineas[-1]}")
except Exception as e:
    print(f"ERROR NOAA: {e}")

