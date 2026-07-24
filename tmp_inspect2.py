import pandas as pd
from pathlib import Path
files = [
    'data/04_model_output/alertas_municipios.parquet',
    'data/04_model_output/cultivos_proyeccion_2029.parquet',
    'data/04_model_output/ira_timeline_completo.parquet',
]
for f in files:
    p = Path(f)
    print('FILE', f, 'exists', p.exists())
    if p.exists():
        df = pd.read_parquet(p)
        print(' shape', df.shape)
        print(' cols', list(df.columns))
        for col in ['divipola','municipio','anio','escenario','nivel_alerta','cultivo','produccion_total_ton','valor','ira_score','ira_level']:
            if col in df.columns:
                print('  col', col, 'non-null', int(df[col].notna().sum()), 'unique', df[col].nunique(dropna=True))
        print(df.head(3).to_dict('records'))
        print('----')
