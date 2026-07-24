import pandas as pd
from pathlib import Path
root = Path(__file__).resolve().parent
for path in sorted((root / 'data' / '04_model_output').glob('*.parquet')):
    print('FILE', path.name)
    try:
        df = pd.read_parquet(path)
    except Exception as e:
        print('  LOAD ERROR', e)
        continue
    print('  shape', df.shape)
    print('  cols', list(df.columns))
    for key in ['divipola', 'cod_dane', 'codigo_mpio', 'codigo_municipio', 'municipio', 'Codigo', 'cod', 'id']:
        if key in df.columns:
            print('   has', key, 'sample', df[key].astype(str).dropna().unique()[:10])
    if 'divipola' in df.columns:
        n = (df['divipola'].astype(str) == '25328').sum()
        print('   25328 rows', n)
    print()