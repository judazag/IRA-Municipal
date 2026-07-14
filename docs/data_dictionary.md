# Diccionario de Datos — IRA Municipal

## ira_municipal_final.parquet

| Campo | Tipo | Descripción | Rango |
|---|---|---|---|
| divipola | str | Código DANE municipio | 5 dígitos |
| municipio | str | Nombre del municipio | — |
| ira_riesgo | float | Score de riesgo IRA (mayor = más riesgo) | 0.19 - 0.87 |
| nivel_ira | str | Nivel de riesgo clasificado | Bajo/Medio/Alto/Crítico |
| score_D1 | float | Score dimensión Producción (rank percentil) | 0 - 1 |
| score_D2 | float | Score dimensión Acceso (rank percentil) | 0 - 1 |
| score_D3 | float | Score dimensión Clima (rank percentil) | 0 - 1 |
| score_D4 | float | Score dimensión Socioeconómico (rank percentil) | 0 - 1 |
| prob_bajo | float | Probabilidad XGBoost nivel Bajo | 0 - 1 |
| prob_medio | float | Probabilidad XGBoost nivel Medio | 0 - 1 |
| prob_alto | float | Probabilidad XGBoost nivel Alto | 0 - 1 |
| prob_critico | float | Probabilidad XGBoost nivel Crítico | 0 - 1 |
| prob_riesgo_severo | float | Prob. nivel Alto + Crítico | 0 - 1 |
| nivel_predicho | str | Nivel predicho por XGBoost | Bajo/Medio/Alto/Crítico |
| cultivo_top1..5 | str | Top 5 cultivos por producción 2024 | — |
| nivel_alerta | str | Nivel de alerta activa | VERDE/AMARILLA/NARANJA/ROJA |

## municipio_features.parquet

| Campo | Tipo | Descripción |
|---|---|---|
| rendimiento_promedio | float | Rendimiento promedio ton/ha (EVA 2024) |
| n_cultivos | int | Número de cultivos únicos (EVA 2024) |
| produccion_total_ton | float | Producción total en toneladas (EVA 2024) |
| score_aptitud_promedio | float | Score aptitud suelos UPRA (0-3) |
| pct_area_no_condicionada | float | % área sin restricciones agrícolas |
| area_riego_bruta_ha | float | Área con infraestructura de riego activa |
| credito_pequeno_cop | float | Crédito Finagro pequeño productor 2024 (COP) |
| flujo_agricola_kg | float | Flujo SIPSA-A grupos agrícolas 2026 Q1 (kg) |
| precipitacion_anual_mm | float | Precipitación normal anual 1991-2020 (mm) |
| temperatura_media_c | float | Temperatura media anual 1991-2020 (°C) |
| ipm_rural | float | Índice de Pobreza Multidimensional rural 2018 (%) |
| indice_informalidad | float | Índice informalidad de tierras departamental |

## ira_timeline_completo.parquet

| Campo | Tipo | Descripción |
|---|---|---|
| divipola | str | Código DANE municipio |
| municipio | str | Nombre del municipio |
| anio | int | Año (2021-2029) |
| escenario | str | Real/Optimista/Base/Pesimista |
| ira_riesgo | float | Score IRA del año/escenario |
| nivel_ira | str | Nivel clasificado |
| nivel_alerta | str | Nivel de alerta para ese año/escenario |
| cultivo_top1..5 | str | Top cultivos (base 2024 para proyecciones) |

## Niveles IRA — Definición

| Nivel | Rango IRA | Descripción |
|---|---|---|
| Bajo | 0.19 - 0.40 | Municipios con buena capacidad productiva y acceso |
| Medio | 0.41 - 0.49 | Municipios con vulnerabilidad moderada |
| Alto | 0.49 - 0.59 | Municipios con vulnerabilidad significativa |
| Crítico | 0.59 - 0.87 | Municipios con riesgo alimentario severo |

## Niveles de Alerta — Criterios

| Nivel | Criterios |
|---|---|
| ROJA | IRA Alto/Crítico + sin riego (<100 ha) + El Niño activo + bajo flujo SIPSA (<50.000 kg) |
| NARANJA | IRA Alto/Crítico + sin riego O bajo flujo SIPSA |
| AMARILLA | IRA Medio + sin riego (<50 ha) + bajo flujo SIPSA (<20.000 kg) |
| VERDE | No cumple criterios de alerta |
