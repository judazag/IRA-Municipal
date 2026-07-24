import pandas as pd, geopandas as gpd
import numpy as np

df_norm_div = pd.read_parquet('data/02_intermediate/normales_con_divipola.parquet')
gdf_mpio = gpd.read_parquet('data/02_intermediate/poligonos_municipales.parquet')
for df in [gdf_mpio, df_norm_div]:
    if 'divipola' in df.columns:
        df['divipola'] = df['divipola'].astype(str).str.strip().str.replace('.', '', regex=False).str.zfill(5)

gdf_mpio['centroide_lon'] = gdf_mpio.geometry.centroid.x
gdf_mpio['centroide_lat'] = gdf_mpio.geometry.centroid.y
precip_mpio = df_norm_div[df_norm_div['parametro'] == 'PRECIPITACIÓN'].groupby('divipola', as_index=False).agg(precipitacion_anual_mm=('anual','mean'))
temp_mpio = df_norm_div[df_norm_div['parametro'] == 'TEMPERATURA MEDIA'].groupby('divipola', as_index=False).agg(temperatura_media_c=('anual','mean'))
mpio_con_precip = gdf_mpio.merge(precip_mpio, on='divipola', how='inner')
mpio_con_temp = gdf_mpio.merge(temp_mpio, on='divipola', how='inner')
print('gdf_mpio shape', gdf_mpio.shape)
print('precip_mpio shape', precip_mpio.shape)
print('temp_mpio shape', temp_mpio.shape)
print('mpio_con_precip shape', mpio_con_precip.shape)
print('mpio_con_temp shape', mpio_con_temp.shape)
print('mpio_con_temp head')
print(mpio_con_temp[['divipola','temperatura_media_c']].head().to_string(index=False))
