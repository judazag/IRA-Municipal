# Fuentes de Datos

## Resumen

| Categoría | Fuentes | Registros | Cobertura |
|---|---|---|---|
| Producción agrícola | EVA, Aptitud suelos UPRA | 3.1M | 1.122 municipios |
| Acceso logístico | SIPSA-A, SIPSA-P, Finagro, Riego | 2.7M | 1.105 municipios |
| Clima | IDEAM estaciones, Normales, NOAA ONI | 35K | 1.121 municipios |
| Socioeconómico | NBI, IPM, Informalidad | 3.4K | 1.122 municipios |
| Geoespacial | MGN DANE 2024, OSM | 1.1K | 1.121 municipios |
| **Total** | **150 datasets** | **~6M** | **99.9%** |

## Detalle por Fuente

### Producción Agrícola
| Dataset | ID | Registros | Período |
|---|---|---|---|
| EVA (Evaluaciones Agropecuarias) | uejq-wxrr | 93,486 | 2019-2024 |
| Aptitud suelos — Café | kwvf-nwea | 508,129 | Estático |
| Aptitud suelos — Cacao | jdjx-qer4 | 169,266 | Estático |
| Aptitud suelos — 15 cultivos más | Varios | 2,348,669 | Estático |
| Frontera Agrícola | fyc7-sbtz | 455,143 | Estático |

### Acceso Logístico
| Dataset | ID | Registros | Período |
|---|---|---|---|
| SIPSA-A (abastecimiento) | CSV local | 767,484 | 2026 Q1 |
| SIPSA-P (precios) | CSV local | 54,042 | 2024 |
| Finagro (créditos) | w3uf-w9ey | 1,906,481 | 2021-2024 |
| Distritos de Riego | rtxu-twjm | 580 activos | Estático |

### Clima
| Dataset | ID | Registros | Período |
|---|---|---|---|
| Estaciones IDEAM | hp9r-jxuu | 9,672 | Estático |
| Normales Climatológicas | nsz2-kzcq | 14,693 | 1991-2020 |
| NOAA ONI (El Niño) | Web fetch | 917 | 1950-2026 |

### Socioeconómico
| Dataset | Fuente | Registros | Período |
|---|---|---|---|
| NBI Censo 2018 | DANE | 1,122 | 2018 |
| IPM Municipal | DANE | 1,122 | 2018 |
| IPM Privaciones (15) | DANE | 1,122 | 2018 |
| Informalidad tierras | hc6u-q778 | 32 dptos | Estático |

### Geoespacial
| Dataset | Fuente | Cobertura |
|---|---|---|
| MGN 2024 | DANE Geoportal | 1,121 municipios |
| Red vial OSM | OpenStreetMap | Muestra 10 mun. |

## Decisiones Metodológicas Clave

1. **NBI excluido del AHP** — correlación 0.83 con IPM (redundancia)
2. **Sin agua excluido** — correlación 0.66 con IPM (capturado en privaciones)
3. **SIPSA-A solo grupos agrícolas** — excluye carnes, lácteos, pescados
4. **Clima imputado por KNN** — distancia promedio 5.6 km (343 mun. sin estación)
5. **Finagro filtrado** — excluye créditos >  (agroindustria urbana)
6. **Rank-based normalization** — insensible a outliers extremos
