import pandas as pd
import requests
import io

url = "https://www.dane.gov.co/files/censo2018/informacion-tecnica/CNPV-2018-NBI.xlsx"
r = requests.get(url, timeout=30)

df = pd.read_excel(
    io.BytesIO(r.content),
    sheet_name="Municipios",
    header=None,
    skiprows=10
)

df.columns = [
    "cod_depto", "nombre_depto", "cod_municipio", "nombre_municipio",
    "nbi_total", "miseria_total", "vivienda_total", "servicios_total",
    "hacinamiento_total", "inasistencia_total", "dependencia_total",
    "nbi_cabecera", "miseria_cabecera", "vivienda_cabecera", "servicios_cabecera",
    "hacinamiento_cabecera", "inasistencia_cabecera", "dependencia_cabecera",
    "nbi_rural", "miseria_rural", "vivienda_rural", "servicios_rural",
    "hacinamiento_rural", "inasistencia_rural", "dependencia_rural",
]

df = df.dropna(subset=["cod_municipio"])

# Convertir a entero para eliminar decimales
df["cod_depto"]     = df["cod_depto"].astype(float).astype(int).astype(str).str.zfill(2)
df["cod_municipio"] = df["cod_municipio"].astype(float).astype(int).astype(str).str.zfill(3)

# DIVIPOLA correcto
df["divipola"] = df["cod_depto"] + df["cod_municipio"]

# Ver filas con cod_municipio == 000 (son totales departamentales)
print("Filas con cod_municipio == 000 (totales departamentales):")
print(df[df["cod_municipio"] == "000"][["divipola", "nombre_municipio"]].head(10))

# Filtrar solo municipios reales
df = df[df["cod_municipio"] != "000"]

print(f"\nFilas después de limpiar: {len(df)}")
print(f"Municipios únicos: {df['divipola'].nunique()}")
print(f"\nMuestra primeras 3 filas:")
print(df[["divipola", "nombre_municipio", "nbi_total", "nbi_rural"]].head(3).to_string())
print(f"\nNBI total — min: {df['nbi_total'].min():.2f} | max: {df['nbi_total'].max():.2f} | promedio: {df['nbi_total'].mean():.2f}")

# Ver municipios con NBI más alto y más bajo
print(f"\nTop 5 mayor NBI:")
print(df.nlargest(5, "nbi_total")[["divipola", "nombre_municipio", "nbi_total"]].to_string())
print(f"\nTop 5 menor NBI:")
print(df.nsmallest(5, "nbi_total")[["divipola", "nombre_municipio", "nbi_total"]].to_string())