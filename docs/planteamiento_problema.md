# Planteamiento del Problema

## Contexto

Colombia es un país con alta diversidad agrícola y una población rural significativa, 
pero enfrenta desafíos estructurales en seguridad alimentaria. Según el DANE (Censo 2018), 
el 27.2% de los hogares rurales tiene NBI y el 51.1% vive en pobreza multidimensional.

## Problema

No existe un instrumento unificado que integre datos de producción agrícola, 
acceso logístico, vulnerabilidad climática y condición socioeconómica a nivel municipal 
para identificar y priorizar municipios en riesgo alimentario.

Los instrumentos existentes tienen limitaciones:
- **SISBEN**: mide pobreza pero no producción agrícola
- **IPM**: mide privaciones pero no acceso logístico
- **PDET**: prioriza municipios post-conflicto pero no todos los vulnerables

## Solución Propuesta

El **IRA-Municipal** (Índice de Riesgo Alimentario Municipal) es un índice compuesto 
que integra 4 dimensiones:

| Dimensión | Peso | Indicadores |
|---|---|---|
| D1 Producción | 35% | Rendimiento, diversificación, aptitud suelos, frontera agrícola |
| D2 Acceso | 30% | Flujo SIPSA, crédito pequeño productor, riego |
| D3 Clima | 15% | Precipitación KNN, temperatura, ONI |
| D4 Socioeconómico | 20% | IPM rural, informalidad tierras |

## Pregunta de Investigación

¿Cuáles municipios de Colombia tienen mayor riesgo de inseguridad alimentaria 
y qué factores determinan ese riesgo?

## Impacto Esperado

- Identificación de 281 municipios en nivel Crítico
- Sistema de alertas tempranas ante El Niño
- Proyección de deterioro 2025-2029 bajo 3 escenarios
- Priorización de intervenciones por costo-efectividad
