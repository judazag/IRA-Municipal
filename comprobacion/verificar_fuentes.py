import requests

resultados = {"ok": [], "error": []}

def check(nombre, url, tipo="soda"):
    try:
        r = requests.get(url, timeout=15)
        if tipo == "soda":
            if r.status_code == 200 and r.json():
                cols = list(r.json()[0].keys())
                print(f"✅ {nombre} — {len(cols)} cols: {cols[:4]}")
                resultados["ok"].append(nombre)
            else:
                print(f"❌ {nombre} — HTTP {r.status_code}")
                resultados["error"].append(nombre)
        elif tipo == "head":
            if r.status_code == 200:
                print(f"✅ {nombre} — HTTP {r.status_code} | {r.headers.get('Content-Type', '?')[:40]}")
                resultados["ok"].append(nombre)
            else:
                print(f"❌ {nombre} — HTTP {r.status_code}")
                resultados["error"].append(nombre)
        elif tipo == "text":
            if r.status_code == 200:
                lineas = r.text.strip().split("\n")
                print(f"✅ {nombre} — {len(lineas)} registros | Última: {lineas[-1].strip()}")
                resultados["ok"].append(nombre)
            else:
                print(f"❌ {nombre} — HTTP {r.status_code}")
                resultados["error"].append(nombre)
    except Exception as e:
        print(f"❌ {nombre} — ERROR: {e}")
        resultados["error"].append(nombre)

# ─── 1. SODA API — datos.gov.co ───────────────────────────────────────────────
print("=" * 60)
print("1. SODA API — datos.gov.co")
print("=" * 60)

soda = {
    "EVA 2019-2023":             "https://www.datos.gov.co/resource/uejq-wxrr.json?$limit=1",
    "Frontera Agrícola":         "https://www.datos.gov.co/resource/fyc7-sbtz.json?$limit=1",
    "Distritos de Riego":        "https://www.datos.gov.co/resource/rtxu-twjm.json?$limit=1",
    "Informalidad de Tierras":   "https://www.datos.gov.co/resource/hc6u-q778.json?$limit=1",
    "Créditos Finagro":          "https://www.datos.gov.co/resource/w3uf-w9ey.json?$limit=1",
    "Red Vial":                  "https://www.datos.gov.co/resource/ie7y-asdn.json?$limit=1",
    "Estaciones IDEAM":          "https://www.datos.gov.co/resource/hp9r-jxuu.json?$limit=1",
    "Normales Climatológicas":   "https://www.datos.gov.co/resource/nsz2-kzcq.json?$limit=1",
    "Aptitud Suelos (muestra)":  "https://www.datos.gov.co/resource/tx7u-frn2.json?$limit=1",
}
for nombre, url in soda.items():
    check(nombre, url, tipo="soda")

# ─── 2. Descarga directa ──────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("2. Descarga directa — DANE")
print("=" * 60)

directos = {
    "SIPSA-A 2018-2025":  "https://microdatos.dane.gov.co/index.php/catalog/697",
    "SIPSA-P 2013-2024":  "https://microdatos.dane.gov.co/index.php/catalog/776",
    "NBI Censo 2018":     "https://www.dane.gov.co/files/censo2018/informacion-tecnica/CNPV-2018-NBI.xlsx",
    "IPM 2024 (ZIP)":     "https://www.datos.gov.co/dataset/Indice-de-Pobreza-Multidimensional-IPM-2024/ntk3-fdqa/about_data",
}
for nombre, url in directos.items():
    check(nombre, url, tipo="head")

# ─── 3. UPRA ArcGIS REST ──────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("3. ArcGIS REST — UPRA")
print("=" * 60)
check(
    "UPRA ArcGIS raíz",
    "https://geoservicios.upra.gov.co/arcgis/rest/services?f=json",
    tipo="head"
)

# ─── 4. APIs Externas ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("4. APIs Externas — Alertas Tempranas")
print("=" * 60)

check("IDEAM DHIME",  "http://dhime.ideam.gov.co/atencionciudadano/", tipo="head")
check("NOAA ONI",     "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt", tipo="text")

# ─── Resumen ──────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("RESUMEN FINAL")
print("=" * 60)
print(f"✅ Accesibles:  {len(resultados['ok'])}  — {resultados['ok']}")
print(f"❌ Con error:   {len(resultados['error'])} — {resultados['error']}")