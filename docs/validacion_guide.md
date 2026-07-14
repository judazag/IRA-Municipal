# Guía de Validación — IRA Municipal

## Reproducibilidad

### Requisitos
- Python 3.11+
- Ver requirements.txt o environment.yml

### Instalación
\\\ash
# Con pip
pip install -r requirements.txt

# Con conda
conda env create -f environment.yml
conda activate ira-municipal
\\\

### Ejecución del pipeline completo
\\\ash
# Ejecutar notebooks en orden
jupyter nbconvert --to notebook --execute notebooks/00_comprension_negocio.ipynb
jupyter nbconvert --to notebook --execute notebooks/01_EDA_exploracion_datos.ipynb
jupyter nbconvert --to notebook --execute notebooks/02_limpieza_transformacion.ipynb
jupyter nbconvert --to notebook --execute notebooks/03_analisis_descriptivo.ipynb
jupyter nbconvert --to notebook --execute notebooks/04_modelo_predictivo.ipynb
jupyter nbconvert --to notebook --execute notebooks/05_reportes_automaticos.ipynb
\\\

## Validación del IRA

### Criterios de éxito
| Métrica | Umbral | Resultado |
|---|---|---|
| CR AHP | < 0.10 | 0.0000 ✅ |
| F1 Macro CV | > 0.70 | 0.7546 ✅ |
| AUC-ROC temporal | > 0.80 | 0.8841 ✅ |
| Sensibilidad pesos | < 15% | 5.3% ✅ |
| Cobertura municipal | > 95% | 99.9% ✅ |

### Validación geográfica
El IRA debe producir estos resultados esperados:

**Municipios esperados en nivel Crítico:**
- La Guajira: Uribia, Manaure, Albania, Hatonuevo ✅
- Chocó: Bagadó, Sipí, Lloró ✅
- Bolívar: Cicuco, Zambrano, Norosí, Arenal ✅
- ANM: Pana Pana, Puerto Colombia, Morichal ✅

**Municipios esperados en nivel Bajo:**
- Eje Cafetero: Pereira, Armenia, Manizales ✅
- Valle del Cauca: Cali, Palmira, Jamundí ✅
- Meta: Villavicencio, Granada ✅

### Validación estadística
- **Índice de Moran I = 0.6251** (p<0.001) — clustering espacial significativo
- **207 municipios HH** — clusters de alto riesgo en zonas conocidas
- **220 municipios LL** — clusters de bajo riesgo en zonas desarrolladas

## Validación del Modelo XGBoost

### Clasificación IRA
\\\python
# Verificar F1 por clase
from sklearn.metrics import classification_report
print(classification_report(y_val, y_pred, 
      target_names=['Bajo','Medio','Alto','Crítico']))
# F1 esperado: Bajo≈0.69, Medio≈0.82, Alto≈0.86, Crítico≈0.66
\\\

### Predicción temporal
\\\python
# Verificar AUC-ROC
from sklearn.metrics import roc_auc_score
auc = roc_auc_score(y_test, y_prob)
# AUC esperado: > 0.88
\\\

## Datos de Entrada Requeridos

| Archivo | Fuente | Frecuencia actualización |
|---|---|---|
| EVA | datos.gov.co (uejq-wxrr) | Anual |
| Finagro | datos.gov.co (w3uf-w9ey) | Mensual |
| SIPSA-A | DANE | Cuatrimestral |
| SIPSA-P | DANE | Mensual |
| NOAA ONI | cpc.ncep.noaa.gov | Mensual |
| NBI/IPM | DANE Censo | Decenal |
| Aptitud suelos | UPRA datos.gov.co | Estático |

## Contacto y Soporte

- **Repositorio**: github.com/judazag/ira-municipal
- **Competencia**: Datos al Ecosistema 2026 — Reto 04
- **Equipo**: Ingeniería de Sistemas — UNAL Bogotá
