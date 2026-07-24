import pandas as pd
from pathlib import Path
files = [
    'data/03_primary/municipio_features.parquet',
    'data/03_primary/ira_municipal_final.parquet',
    'data/02_intermediate/municipio_features.parquet',
    'data/02_intermediate/ira_municipal_final.parquet',
]
for f in files:
    p = Path(f)
    if not p.exists():
        print('MISSING', f)
        continue
    try:
        df = pd.read_parquet(p)
        print('FILE', f)
        print(' rows', len(df))
        print(' cols', list(df.columns))
        for col in ['divipola','municipio','ira_score','ira_level','nivel_ira','ira_riesgo','ira']:
            if col in df.columns:
                print('  col', col, 'non-null', int(df[col].notna().sum()), 'unique', df[col].nunique(dropna=True))
        cols = [c for c in ['divipola','municipio','ira_score','ira_level','nivel_ira','ira_riesgo','ira'] if c in df.columns]
        if cols:
            print(' sample', df[cols].head(10).to_dict('records'))
        print('-----')
    except Exception as e:
        print('ERROR reading', f, e)
