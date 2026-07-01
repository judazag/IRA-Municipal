import requests

datasets = {
    # SODA
    "uejq-wxrr": "EVA 2019-2023",
    "fyc7-sbtz":  "Frontera Agrícola",
    "rtxu-twjm":  "Distritos de Riego",
    "hc6u-q778":  "Informalidad de Tierras",
    "w3uf-w9ey":  "Créditos Finagro",
    "ie7y-asdn":  "Red Vial",
    "hp9r-jxuu":  "Estaciones IDEAM",
    "nsz2-kzcq":  "Normales Climatológicas",
    "tx7u-frn2":  "Aptitud Suelos (muestra)",
}

for dataset_id, nombre in datasets.items():
    print(f"\n{'='*60}")
    print(f"{nombre} ({dataset_id})")
    print(f"{'='*60}")

    # Todas las columnas con valor de muestra
    url = f"https://www.datos.gov.co/resource/{dataset_id}.json?$limit=1"
    r = requests.get(url, timeout=10)
    if r.status_code == 200 and r.json():
        fila = r.json()[0]
        print(f"Columnas ({len(fila)}):")
        for col, val in fila.items():
            print(f"  {col}: {str(val)[:80]}")
    else:
        print(f"❌ HTTP {r.status_code}")
        continue

    # Total de registros
    url_count = f"https://www.datos.gov.co/resource/{dataset_id}.json?$select=count(*)"
    r2 = requests.get(url_count, timeout=10)
    if r2.status_code == 200:
        print(f"\nTotal registros: {r2.json()[0].get('count', '?')}")