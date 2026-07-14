# Marco Metodológico

## Enfoque CRISP-DM

El proyecto sigue la metodología CRISP-DM (Cross-Industry Standard Process for Data Mining):

| Fase | Notebook | Descripción |
|---|---|---|
| 1. Comprensión negocio | 00 | Definición del IRA y criterios de éxito |
| 2. Comprensión datos | 01 | EDA de 150 datasets verificados |
| 3. Preparación datos | 02-03 | Limpieza, feature construction, normalización |
| 4. Modelado | 04 | AHP + XGBoost multiclase |
| 5. Evaluación | 04 | SHAP, Moran I, sensibilidad |
| 6. Despliegue | 05 | API, frontend, reportes |

## Método AHP (Analytic Hierarchy Process)

### Matriz de Comparación Pareada
Basada en la escala de Saaty (1-9), derivada matemáticamente para obtener 
pesos exactos 35/30/15/20:

| | D1 | D2 | D3 | D4 |
|---|---|---|---|---|
| D1 | 1.000 | 1.167 | 2.333 | 1.750 |
| D2 | 0.857 | 1.000 | 2.000 | 1.500 |
| D3 | 0.429 | 0.500 | 1.000 | 0.750 |
| D4 | 0.571 | 0.667 | 1.333 | 1.000 |

**CR = 0.0000** — Consistencia perfecta (umbral aceptable: CR < 0.10)

### Normalización Rank-Based
Se adoptó normalización por percentil en lugar de Min-Max debido a:
- Skewness extremo en producción (3.50) y aptitud suelos (7.03)
- Sensibilidad a outliers del Valle del Cauca y Meta
- Distribución uniforme resultante (skewness ≈ 0 en todos los indicadores)

### Análisis de Sensibilidad
Variando pesos ±20%, el máximo cambio de nivel es **5.3%** de municipios.
Umbral de robustez: < 15%. El índice es **ROBUSTO**.

## Modelo XGBoost

### Clasificación IRA (multiclase)
- **Target**: nivel IRA (Bajo/Medio/Alto/Crítico)
- **Features**: 35 (11 rank AHP + 14 privaciones IPM + 8 SIPSA-P + ONI + informalidad)
- **Validación**: 5-fold estratificado
- **F1 Macro CV**: 0.7546

### Predicción Temporal
- **Target**: deterioro de nivel año a año (binario)
- **Features**: scores por dimensión + IRA actual + ONI
- **AUC-ROC CV**: 0.8841
- **Desbalance**: 1:20 — manejado con scale_pos_weight

### Simulación de Escenarios 2025-2029
Tres escenarios definidos por deltas sobre indicadores dinámicos:

| Escenario | Rendimiento | Crédito | Riego | ONI |
|---|---|---|---|---|
| Optimista | +10%/año | +15%/año | +20%/año | -0.84 |
| Base | 0% | 0% | 0% | 0.00 |
| Pesimista | -10%/año | -15%/año | 0% | +0.96 |

## Autocorrelación Espacial

**Índice de Moran I = 0.6251** (p < 0.001, z = 34.98)

Autocorrelación espacial positiva muy significativa — los municipios con IRA similar 
tienden a agruparse geográficamente. Clusters LISA identificados:
- **HH (Alto-Alto)**: 207 municipios — La Guajira, Chocó, Bolívar
- **LL (Bajo-Bajo)**: 220 municipios — Eje Cafetero, Valle, Cundinamarca
