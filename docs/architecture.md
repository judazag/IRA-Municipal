# Arquitectura del Sistema

## Stack Tecnológico

### Data Pipeline
- **Python 3.11** — lenguaje principal
- **sodapy** — ingesta SODA API (datos.gov.co)
- **pandas / geopandas** — transformación y análisis espacial
- **pyarrow / parquet** — almacenamiento staging
- **osmnx** — red vial OpenStreetMap
- **scikit-learn / xgboost / shap** — modelado y explicabilidad
- **esda / libpysal** — autocorrelación espacial

### Backend
- **FastAPI** — API REST
- **SQLAlchemy + GeoAlchemy2** — ORM con soporte espacial
- **PostgreSQL + PostGIS** — base de datos
- **Docker** — contenedorización

### Frontend
- **Next.js** — framework React
- **Leaflet / Mapbox GL JS** — mapa interactivo
- **TypeScript** — tipado estático

### Despliegue
- **Railway** — backend y base de datos
- **Vercel** — frontend

## Estructura del Repositorio

\\\
ira-municipal/
├── notebooks/          # Pipeline CRISP-DM (00-05)
├── src/                # Código fuente modular
│   ├── config.py       # Configuración
│   ├── logger.py       # Logging
│   ├── db.py           # Conexión BD
│   ├── data_ingestion.py
│   ├── data_cleaning.py
│   └── pipeline_integration.py
├── data/
│   ├── 01_raw/         # Datos originales
│   ├── 02_intermediate/ # Datos limpios
│   ├── 03_primary/     # Features construidas
│   └── 04_model_output/ # Resultados del modelo
├── backend/            # FastAPI
├── frontend/           # Next.js
├── reports/
│   └── figures/        # 34 gráficas generadas
├── docs/               # Documentación
├── tests/              # Tests unitarios
├── requirements.txt
└── environment.yml
\\\

## Flujo de Datos

\\\
datos.gov.co / DANE / NOAA
        ↓ (sodapy / requests)
01_raw/ — datos originales
        ↓ (notebook 02)
02_intermediate/ — datos limpios (19 archivos, 175 MB)
        ↓ (notebook 03)
03_primary/ — features construidas (12 archivos, 1.2 MB)
        ↓ (notebook 04)
04_model_output/ — IRA + predicciones (15 archivos)
        ↓ (FastAPI)
API REST → Frontend → Usuario final
\\\

## Endpoints API

| Endpoint | Descripción |
|---|---|
| GET /healthz | Estado del servicio |
| GET /municipios | Lista municipios con IRA |
| GET /municipios/geojson | GeoJSON para el mapa |
| GET /municipios/{divipola} | Detalle de un municipio |
| GET /municipios/{divipola}/dimensiones | Scores por dimensión |
| GET /municipios/{divipola}/cultivos | Top cultivos |
| GET /municipios/{divipola}/cultivos/historico | EVA 2019-2024 |
| GET /timeline/geojson | GeoJSON por año y escenario |
| GET /alertas | Municipios en alerta |
| GET /metrics | Métricas nacionales |
