import sys
sys.path.insert(0, "F:/Proyectos/IRA-Municipal")

from pipeline.ingesta.soda.conector_soda import ConectorSODA

with ConectorSODA() as soda:
    df = soda.descargar_y_guardar(
        dataset_id="uejq-wxrr",
        nombre="eva_2019_2023",
        fuente="eva",
        columnas=[
            "c_digo_dane_municipio",
            "municipio",
            "departamento",
            "cultivo",
            "a_o",
            "rea_sembrada",
            "rea_cosechada",
            "producci_n",
            "rendimiento",
        ],
    )

print(f"\nRegistros: {len(df):,}")
print(f"Columnas: {list(df.columns)}")
print(f"\nMuestra:")
print(df.head(3).to_string())