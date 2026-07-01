import pandas as pd

ruta = "comprobacion/csv/anexo-censal-pobreza-municipal-2018.xlsx"  # ajusta la ruta

# ─── Hoja principal — IPM total + rural ───────────────────────────────────────
print("=" * 60)
print("IPM Municipal — Hoja dominios")
print("=" * 60)
df_ipm = pd.read_excel(
    ruta,
    sheet_name="4_IPM Mpio dominios",
    header=0,  # encabezados en fila 0
    dtype={"ID": str}  # DIVIPOLA como string para no perder ceros
)

# Renombrar columnas
df_ipm.columns = ["divipola", "municipio", "ipm_total", "ipm_cabecera", "ipm_rural"]

# Limpiar
df_ipm = df_ipm.dropna(subset=["divipola"])
df_ipm["divipola"] = df_ipm["divipola"].str.zfill(5)


print(f"Municipios: {df_ipm['divipola'].nunique()}")
print(f"\nColumnas: {list(df_ipm.columns)}")
print(f"\nMuestra:")
print(df_ipm.head(3).to_string())
print(f"\nIPM total — min: {df_ipm['ipm_total'].min()} | max: {df_ipm['ipm_total'].max()} | promedio: {df_ipm['ipm_total'].mean():.1f}")
print(f"IPM rural — min: {df_ipm['ipm_rural'].min()} | max: {df_ipm['ipm_rural'].max()} | promedio: {df_ipm['ipm_rural'].mean():.1f}")

print(f"\nTop 5 mayor IPM rural:")
print(df_ipm.nlargest(5, "ipm_rural")[["divipola", "municipio", "ipm_rural"]].to_string())
print(f"\nTop 5 menor IPM rural:")
print(df_ipm.nsmallest(5, "ipm_rural")[["divipola", "municipio", "ipm_rural"]].to_string())

# ─── Hoja privaciones — features para XGBoost ─────────────────────────────────
print("\n" + "=" * 60)
print("IPM Privaciones — Features XGBoost")
print("=" * 60)
df_priv = pd.read_excel(
    ruta,
    sheet_name="6_Privaciones IPM Dpt-Mpio",
    header=1,  # encabezados en fila 1
    dtype={"ID": str}
)

df_priv = df_priv.dropna(subset=["ID"])
df_priv["ID"] = df_priv["ID"].str.zfill(5)
df_priv = df_priv.rename(columns={"ID": "divipola", "Municipio": "municipio"})

print(f"Municipios: {df_priv['divipola'].nunique()}")
print(f"Privaciones disponibles ({len(df_priv.columns) - 2}):")
for col in df_priv.columns[2:]:
    print(f"  {col}")
print(f"\nMuestra fila 1:")
print(df_priv.iloc[0].to_dict())