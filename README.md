# IRA-Municipal 🌾
## Índice de Riesgo Alimentario para Colombia

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+PostGIS-blue)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Datos Abiertos](https://img.shields.io/badge/Datos-datos.gov.co-orange)](https://datos.gov.co)

> Proyecto desarrollado para el concurso **Datos al Ecosistema 2026: IA para Colombia**
> Reto 04 — Agricultura y Desarrollo Rural | Ministerio TIC

---

## 🎯 Problema

Colombia tiene **14,4 millones de personas en inseguridad alimentaria**, pero no existe un instrumento que permita identificar cuáles municipios están al borde del colapso alimentario ni por qué. Las instituciones toman decisiones de focalización con información parcial, desactualizada y no integrada.

## 💡 Solución

El **IRA-Municipal** construye un índice compuesto que cruza **150 bases de datos abiertas** del Estado colombiano para calcular un nivel de riesgo alimentario (**Bajo / Medio / Alto / Crítico**) para cada uno de los **1.104 municipios** del país.

El resultado es:
- 🗺️ **Mapa interactivo** de riesgo alimentario municipal
- 📊 **Dashboard** de seguimiento histórico por municipio
- 🚨 **Sistema de alertas tempranas** automático ante fenómenos climáticos IDEAM

---

## 📊 Fuentes de Datos

| Dimensión | Fuentes | Datasets |
|---|---|---|
| Producción agrícola | EVA-UPRA, Aptitud de suelos UPRA | 137 |
| Acceso logístico | SIPSA-A DANE, Red vial OSM | 2 |
| Vulnerabilidad climática | Estaciones IDEAM, Normales Climatológicas, NOAA ONI | 3 |
| Socioeconómico | IPM Censal 2018, NBI Censo 2018 | 2 |
| Infraestructura | Distritos de Riego, Créditos Finagro, Frontera Agrícola | 3 |
| Contexto | Informalidad de Tierras, SIPSA-P | 2 |
| **Total** | | **150 datasets** |

---

## 🔬 Metodología — CRISP-DM

| Fase | Estado | Descripción |
|---|---|---|
| 1. Comprensión del negocio | ✅ Completa | Definición del problema, criterios de éxito, audiencia objetivo |
| 2. Comprensión de los datos | ✅ Completa | 150 datasets verificados, 5 decisiones metodológicas resueltas |
| 3. Preparación de datos | 🔄 En progreso | Pipeline de ingesta, limpieza, tabla maestra municipio_features |
| 4. Modelado | ⏳ Pendiente | AHP para índice compuesto + XGBoost para predicción |
| 5. Evaluación | ⏳ Pendiente | Validación contra casos conocidos, análisis de sensibilidad |
| 6. Despliegue | ⏳ Pendiente | FastAPI + Next.js + Railway + Vercel |

---

## 🏗️ Arquitectura

\\\
[APIs datos.gov.co / IDEAM / NOAA / OSM]
              ↓
     [src/data_ingestion.py]
              ↓
     [src/data_cleaning.py]
              ↓
  [src/feature_engineering.py]
     AHP (índice) + XGBoost (predicción)
              ↓
     [PostgreSQL + PostGIS]
              ↓
  [backend/FastAPI REST API]
              ↓
  [frontend/Next.js + Mapbox GL JS]
\\\

---

## 🚀 Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Ingesta | Python 3.11 + sodapy + requests + osmnx |
| Transformación | pandas + geopandas + scikit-learn |
| Modelado | AHP (implementación propia) + XGBoost |
| Almacenamiento | PostgreSQL 15 + PostGIS |
| Backend | FastAPI + SQLAlchemy |
| Frontend | Next.js 14 + TypeScript + Mapbox GL JS |
| Visualización | Recharts + Plotly |

---

## 📁 Estructura del Repositorio

\\\
ira-municipal/
├── src/                    # Código fuente modularizado
│   ├── config.py           # Configuración y variables de entorno
│   ├── data_ingestion.py   # Conectores a todas las fuentes
│   ├── data_cleaning.py    # Limpieza y estandarización
│   ├── feature_engineering.py  # AHP + normalización
│   ├── pipeline_integration.py # Tabla maestra + alertas
│   ├── model_training.py   # XGBoost
│   └── model_evaluation.py # Métricas y validación
├── notebooks/              # Análisis exploratorio y experimentación
├── data/                   # Datos por etapa (no versionado)
├── models/                 # Artefactos del modelo
├── docs/                   # Documentación técnica CRISP-DM
├── reports/                # Reportes y visualizaciones
├── backend/                # API REST FastAPI
├── frontend/               # Aplicación web Next.js
├── pipelines/              # Orquestación del pipeline
└── tests/                  # Pruebas de calidad y modelo
\\\

---

## ⚙️ Instalación

\\\ash
# Clonar el repositorio
git clone https://github.com/tu-usuario/ira-municipal.git
cd ira-municipal

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Correr pipeline completo
python pipelines/pipeline_ml.py
\\\

---

## 👥 Equipo

| Rol | Perfil | Responsabilidad |
|---|---|---|
| Líder técnico | Ing. Sistemas — ML/Data | Pipeline, modelos AHP + XGBoost, backend FastAPI |
| Desarrollador | Ing. Sistemas — Fullstack | Frontend Next.js, Mapbox, deploy |
| Dominio | Ing. Agrónomo | Validación agronómica, indicadores EVA, impacto |

---

## 🔗 Links

- [Concurso Datos al Ecosistema 2026](https://datos.gov.co/stories/s/Concurso-Datos-al-Ecosistema-2026-IA-para-Colombia/ddau-8cy9/)
- [Portal de Datos Abiertos Colombia](https://datos.gov.co)
- [Documentación técnica](docs/)
- [Publicación en datos.gov.co](https://herramientas.datos.gov.co/usos)
