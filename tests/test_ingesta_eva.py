import sys
sys.path.insert(0, "F:/Proyectos/IRA-Municipal")

from pipeline.ingesta.soda.ingesta_eva import ejecutar

df = ejecutar()

print(f"\nRegistros: {len(df):,}")
print(f"Municipios únicos: {df['divipola'].nunique():,}")
print(f"Años disponibles: {sorted(df['anio'].dropna().unique().tolist())}")
print(f"Cultivos únicos: {df['cultivo'].nunique():,}")
print(f"\nMuestra:")
print(df[["divipola", "municipio", "cultivo", "anio", "produccion_ton", "rendimiento_ton_ha"]].head(5).to_string())
