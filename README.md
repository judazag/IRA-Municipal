# IRA-Municipal 🌾
## Índice de Riesgo Alimentario para Colombia

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+PostGIS-blue)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> Proyecto desarrollado para el concurso **Datos al Ecosistema 2026: IA para Colombia**
> Reto 04 — Agricultura y Desarrollo Rural | Ministerio TIC

---

## 🎯 ¿Qué es el IRA-Municipal?

Colombia tiene 14,4 millones de personas en inseguridad alimentaria, pero no existe un instrumento que permita identificar cuáles municipios están al borde del colapso alimentario ni por qué.

El **IRA-Municipal** construye un índice compuesto que cruza **150 bases de datos abiertas** del Estado colombiano para calcular un nivel de riesgo alimentario (**Bajo / Medio / Alto / Crítico**) para cada uno de los **1.104 municipios** del país.

---

## 🏗️ Arquitectura

\\\
APIs datos.gov.co / IDEAM / NOAA
         ↓
   [Ingesta Python + sodapy]
         ↓
   [Transformación pandas + geopandas]
         ↓
   [Cálculo AHP + XGBoost]
         ↓
   [PostgreSQL + PostGIS]
         ↓
   [FastAPI Backend]
         ↓
   [Next.js Frontend — Mapa + Dashboard + Alertas]
\\\

---

## 📊 Fuentes de Datos

| Dimensión | Fuentes |
|---|---|
| Producción agrícola | EVA 2019-2023 (UPRA), 136 datasets de aptitud de suelos |
| Acceso logístico | SIPSA-A 2018-2026 (DANE), Red vial OSM |
| Vulnerabilidad climática | Estaciones IDEAM, Normales Climatológicas, NOAA ONI |
| Socioeconómico | IPM Municipal 2018, NBI Censo 2018 (DANE) |
| Infraestructura | Distritos de Riego, Créditos Finagro, Frontera Agrícola |

---

## 🔬 Metodología

- **CRISP-DM** como marco estructurador del desarrollo
- **AHP (Analytic Hierarchy Process)** para construcción del índice compuesto
- **XGBoost** para modelo predictivo de deterioro del IRA
- **Análisis de sensibilidad ±20%** para verificar robustez del índice

---

## 🚀 Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Ingesta | Python 3.11 + sodapy + requests |
| Transformación | pandas + geopandas + osmnx |
| Modelado | pyahp + XGBoost + scikit-learn |
| Almacenamiento | PostgreSQL 15 + PostGIS |
| Orquestación | Apache Airflow |
| Backend | FastAPI + SQLAlchemy |
| Frontend | Next.js 14 + TypeScript + Mapbox GL JS |
| Deploy | Docker + Railway + Vercel |

---

## 📁 Estructura del Repositorio

\\\
ira-municipal/
├── pipeline/           # Pipeline de datos (ingesta, transformación, cálculo)
│   ├── ingesta/        # Conectores por fuente (SODA, descarga, OSM, APIs)
│   ├── transformacion/ # Limpieza y estandarización
│   ├── calculo/        # AHP + XGBoost
│   ├── alertas/        # Sistema de alertas tempranas IDEAM
│   └── utils/          # Funciones compartidas
├── backend/            # API REST FastAPI
├── frontend/           # Aplicación web Next.js
├── airflow/            # DAGs de orquestación
├── database/           # Migraciones PostgreSQL + PostGIS
├── data/               # Datos staging (no versionado)
└── docs/               # Documentación técnica CRISP-DM
\\\

---

## ⚙️ Instalación

### Prerrequisitos
- Python 3.11+
- Docker + Docker Compose
- Node.js 18+

### Setup local

\\\ash
# Clonar el repositorio
git clone https://github.com/tu-usuario/ira-municipal.git
cd ira-municipal

# Copiar variables de entorno
cp .env.example .env

# Levantar servicios
docker-compose up -d

# Instalar dependencias Python
pip install -r pipeline/requirements.txt

# Correr verificación de fuentes
python pipeline/utils/verificar_fuentes.py
\\\

---

## 👥 Equipo

| Rol | Responsabilidad |
|---|---|
| Líder técnico (Ing. Sistemas) | Pipeline de datos, modelos AHP + XGBoost, backend FastAPI |
| Ing. Sistemas | Frontend Next.js, Mapbox, deploy Railway + Vercel |
| Ing. Agrónomo | Validación de dominio, indicadores EVA, narrativa de impacto |

---

## 📅 Cronograma

| Fase CRISP-DM | Estado |
|---|---|
| Fase 1 — Comprensión del negocio | ✅ Completa |
| Fase 2 — Comprensión de los datos | ✅ Completa |
| Fase 3 — Preparación de datos | 🔄 En progreso |
| Fase 4 — Modelado | ⏳ Pendiente |
| Fase 5 — Evaluación | ⏳ Pendiente |
| Fase 6 — Despliegue | ⏳ Pendiente |

---

## 📄 Licencia

MIT License — ver [LICENSE](LICENSE) para más detalles.

---

## 🔗 Links

- [Concurso Datos al Ecosistema 2026](https://datos.gov.co/stories/s/Concurso-Datos-al-Ecosistema-2026-IA-para-Colombia/ddau-8cy9/)
- [Portal de Datos Abiertos Colombia](https://datos.gov.co)
- [Documentación técnica](docs/)
