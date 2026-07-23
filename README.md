# IRA-Municipal — Índice de Riesgo Alimentario Municipal

> **Datos al Ecosistema 2026: IA para Colombia — Reto 04 Agricultura y Desarrollo Rural**

## ¿Qué es el IRA-Municipal?

El IRA-Municipal es un índice compuesto que clasifica los **1.122 municipios de Colombia** 
según su riesgo de inseguridad alimentaria, integrando datos de producción agrícola, 
acceso logístico, vulnerabilidad climática y condición socioeconómica.

## 🚀 Demo

- **Herramienta interactiva**: [URL del frontend desplegado]
- **API pública**: [URL del backend desplegado]/docs
- **Dataset IRA**: [reports/ira_municipal_2024.csv](reports/ira_municipal_2024.csv)

## 📊 Resultados Clave

| Métrica | Valor |
|---|---|
| Municipios analizados | 1.122 |
| Municipios en nivel Crítico | 281 (25%) |
| Municipios en Alerta ROJA | 340 (30.3%) |
| Producción nacional en riesgo | 9.23M ton (14.1%) |
| CR AHP (consistencia) | 0.0000 |
| F1 Macro XGBoost | 0.7546 |
| AUC-ROC predicción temporal | 0.8841 |
| Índice de Moran (clustering) | 0.6251*** |

## 🏗️ Arquitectura

```bash
datos.gov.co / DANE / NOAA ONI
↓ sodapy / requests
02_intermediate/ — 19 fuentes limpias (175 MB)
↓ feature engineering
03_primary/ — tabla maestra 1.122 × 48 features
↓ AHP + XGBoost
04_model_output/ — IRA + predicciones + alertas
↓ FastAPI
API REST → Mapa interactivo → Usuario final

```

## 📁 Estructura del Repositorio

```bash
ira-municipal/
├── notebooks/ # Pipeline CRISP-DM
│ ├── 00_comprension_negocio.ipynb
│ ├── 01_EDA_exploracion_datos.ipynb
│ ├── 02_limpieza_transformacion.ipynb
│ ├── 03_analisis_descriptivo.ipynb
│ ├── 04_modelo_predictivo.ipynb
│ └── 05_reportes_automaticos.ipynb
├── src/ # Código fuente modular
├── backend/ # FastAPI
├── frontend/ # Next.js + Leaflet
├── data/ # Pipeline de datos
├── reports/ # Gráficas y CSVs
└── docs/ # Documentación
```

## ⚙️ Instalación

```bash
# Clonar repositorio
git clone https://github.com/judazag/IRA-Municipal.git
cd IRA-Municipal

# Instalar dependencias
pip install -r requirements.txt

# O con conda
conda env create -f environment.yml
conda activate ira-municipal
```

## 🔄 Ejecutar el Pipeline

```bash
# Ejecutar notebooks en orden
jupyter nbconvert --to notebook --execute notebooks/02_limpieza_transformacion.ipynb
jupyter nbconvert --to notebook --execute notebooks/03_analisis_descriptivo.ipynb
jupyter nbconvert --to notebook --execute notebooks/04_modelo_predictivo.ipynb
jupyter nbconvert --to notebook --execute notebooks/05_reportes_automaticos.ipynb
```

## 🗺️ Dimensiones del IRA

| Dimensión | Peso | Indicadores |
|---|---|---|
| D1 Producción | 35% | Rendimiento, diversificación, aptitud suelos, frontera agrícola |
| D2 Acceso | 30% | Flujo SIPSA agrícola, crédito pequeño productor, riego |
| D3 Clima | 15% | Precipitación KNN, temperatura KNN, ONI |
| D4 Socioeconómico | 20% | IPM rural, informalidad de tierras |

## 📡 API Endpoints

```bash

GET /municipios — Lista municipios con IRA
GET /municipios/geojson — GeoJSON para el mapa
GET /municipios/{divipola} — Detalle de un municipio
GET /municipios/{divipola}/cultivos — Top cultivos
GET /municipios/{divipola}/cultivos/historico — EVA 2019-2024
GET /timeline/geojson?escenario=Base&anio=2024 — Mapa por año
GET /alertas — Municipios en alerta
GET /metrics — Métricas nacionales

```

## 🔮 Proyección 2025-2029

| Escenario | Críticos 2024 | Críticos 2029 | Cambio |
|---|---|---|---|
| Optimista | 281 | 167 | -114 (-41%) |
| Base | 281 | 281 | 0 |
| Pesimista | 281 | 388 | +107 (+38%) |

## 📦 Fuentes de Datos

- **EVA** — Evaluaciones Agropecuarias Municipales (datos.gov.co)
- **Finagro** — Créditos agropecuarios 2021-2024 (datos.gov.co)
- **SIPSA** — Sistema de Información de Precios y Abastecimiento (DANE)
- **IDEAM** — Estaciones y normales climatológicas (datos.gov.co)
- **NOAA ONI** — Índice Oceánico El Niño (cpc.ncep.noaa.gov)
- **UPRA** — Aptitud de suelos 17 cultivos (datos.gov.co)
- **DANE** — NBI, IPM, MGN 2024, Informalidad

## 👥 Equipo

- **Juan Camilo Daza gutierrez** 
- **Andres Felipe Poveda Bellon** 
- **Estefanía Marín Páez** 

## 📄 Licencia

MIT License — Ver [LICENSE](LICENSE)

---
*Datos al Ecosistema 2026: IA para Colombia — Reto 04 Agricultura y Desarrollo Rural*
*Universidad Nacional de Colombia — Bogotá*
"@ | Set-Content -Path README.md -Encoding UTF8