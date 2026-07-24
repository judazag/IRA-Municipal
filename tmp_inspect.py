import pandas as pd
import geopandas as gpd
import numpy as np
from pathlib import Path

print('Reading parquet files...')
df_norm_div = pd.read_parquet('data/02_intermediate/normales_con_divipola.parquet')
print(df_norm_div.head().to_string())
print('\nColumns:', list(df_norm_div.columns))
print('\nShape:', df_norm_div.shape)
print('\nParam values:', df_norm_div['parametro'].dropna().unique().tolist())
print('\nDivipola samples:', df_norm_div['divipola'].dropna().astype(str).head(20).tolist())
print('\nUnique divipola count:', df_norm_div['divipola'].dropna().nunique())
