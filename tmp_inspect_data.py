import pandas as pd
from pathlib import Path
root = Path('.').resolve()
for path in sorted((root / 'data' / '04_model_output').glob('*.parquet')):
    if path.name not in [
        'cultivos_proyeccion_2029.parquet',
        'cultivos_en_riesgo.parquet',
        'cultivos_riesgo_historico.parquet',
        'eva_historico_municipios.parquet',
        'alertas_municipios.parquet',
        'ira_municipal_final.parquet',
        'ira_timeline_completo.parquet',
    ]:
        continue
    print('FILE', path.name)
    try:
        df = pd.read_parquet(path)
    except Exception as exc:
        print('  LOAD ERROR', exc)
        continue
    print('  shape', df.shape)
    print('  cols', list(df.columns))
    for col in ['divipola', 'cod_dane', 'cod_mpio', 'codigo_mpio', 'codigo_municipio', 'MPIO', 'municipio', 'Municipio', 'código', 'cod_dane_mpio']:
        if col in df.columns:
            print('   has', col, 'sample', df[col].astype(str).dropna().unique()[:10])
    if 'divipola' in df.columns:
        print('   25328 rows', int((df['divipola'].astype(str) == '25328').sum()))
    else:
        for col in ['cod_dane', 'cod_mpio', 'codigo_mpio', 'codigo_municipio']:
            if col in df.columns:
                print('   25328 rows via', col, int((df[col].astype(str) == '25328').sum()))
    print()