# Descripción de los datos — Actividad 5

## 1. Fuentes de datos identificadas
| Fuente | Qué aporta | Uso en el proyecto |
|---|---|---|
| Sistema experto propio (`knowledge_base.py`, motor de reglas, A*) | Estaciones, líneas, tiempos y rutas óptimas | **Usada**: atributos de cada ruta |
| TransMilenio S.A. (datos abiertos / GTFS) | Estaciones, rutas, validaciones por franja | Fuente real recomendada para reemplazar la base de conocimiento |
| Datos Abiertos Bogotá | Demanda por troncal y estación | Para calibrar los patrones de ocupación |
| IDEAM | Precipitación | Relación lluvia-demanda |

Los datos públicos disponibles son agregados (por estación/franja), no viajes
individuales. Por eso se **desarrolló un dataset sintético** (permitido por el
enunciado cuando no existen las fuentes), reproducible con la semilla 42.

## 2. Cómo se genera `data/viajes_transmilenio.csv` (3000 filas)
1. Se calculan con A* las rutas óptimas entre todos los pares de estaciones.
2. Para cada viaje se elige un par origen-destino al azar y se simula el contexto
   (hora, día, festivo, lluvia).
3. La etiqueta `ocupacion` se obtiene de un puntaje de demanda (hora pico en día
   hábil, lluvia, transbordos, estaciones, domingo/festivo, madrugada/noche) más
   ruido aleatorio, y se discretiza en baja / media / alta.

## 3. Columnas
| Columna | Tipo | Descripción |
|---|---|---|
| origen, destino | texto | Estaciones del viaje (no se usan como atributos del modelo) |
| hora | int 4–22 | Hora de salida |
| dia_semana | int 0–6 | 0 = lunes … 6 = domingo |
| es_festivo | 0/1 | Día festivo |
| lluvia | 0/1 | Hay lluvia |
| linea_inicial | texto | Troncal del primer tramo (de A*) |
| minutos_base | float | Tiempo total de la ruta óptima (de A*) |
| num_estaciones | int | Tramos recorridos (de A*) |
| num_transbordos | int | Transbordos de la ruta (de A*) |
| transbordos_atravesados | int | Estaciones de transbordo intermedias (del motor de reglas) |
| **ocupacion** | baja/media/alta | **Variable objetivo** |

Atributos derivados al preparar los datos: `es_habil`, `es_hora_pico` y variables
dummy de `linea_inicial`.

## 4. Modelo
`DecisionTreeClassifier` (criterio entropía, profundidad máx. 6, mínimo 15 muestras
por hoja, `class_weight="balanced"`), partición 80/20 estratificada y validación
cruzada de 5 pliegues. Resultados en `docs/resultados_modelo.txt` y reglas en
`docs/reglas_arbol.txt`.

## 5. Limitaciones
- La etiqueta es simulada: el modelo aprende el patrón que se programó, no la
  demanda real. Con datos reales de validaciones, el mismo código sirve cambiando
  solo `generar_dataset`.
- La red es una versión simplificada de TransMilenio (ver `knowledge_base.py`).
