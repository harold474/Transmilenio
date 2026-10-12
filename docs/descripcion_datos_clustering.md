# Descripción de los datos — Actividad 6 (aprendizaje no supervisado)

## 1. Problema
Segmentar las estaciones de la red troncal en grupos con comportamiento similar,
**sin etiquetas previas**, para apoyar decisiones como dónde reforzar flota o qué
estaciones tratar como nodos críticos.

## 2. Fuentes de datos identificadas
| Fuente | Qué aporta | Uso en el proyecto |
|---|---|---|
| Sistema experto propio (`knowledge_base.py`, motor de reglas, A*) | Líneas, estaciones, coordenadas relativas y rutas óptimas | **Usada**: atributos estructurales de cada estación |
| TransMilenio S.A. (datos abiertos / GTFS) | Estaciones, rutas, validaciones por estación y franja | Fuente real recomendada para reemplazar la demanda simulada |
| Datos Abiertos Bogotá | Demanda por troncal y estación | Calibrar los niveles de demanda por franja |

Los datos públicos disponibles son agregados y no coinciden con la red simplificada del
proyecto, por lo que se **desarrolló un dataset** (permitido por el enunciado): la parte
estructural sale del sistema experto y la demanda por franja es **sintética**, reproducible
con la semilla 42.

## 3. Dataset `data/estaciones_features.csv` (33 filas, una por estación)
| Columna | Origen | Descripción |
|---|---|---|
| estacion | Base de conocimiento | Nombre de la estación |
| num_lineas | Motor de reglas | Líneas que pasan por la estación (≥ 2 = transbordo) |
| grado | Grafo del motor de reglas | Estaciones vecinas directas |
| intermediacion | A* sobre todos los pares | Fracción de rutas óptimas que pasan por la estación como parada intermedia |
| dist_centro_km | Coordenadas | Distancia a AvenidaJimenez (centro) |
| pico_am, pico_pm, valle, fin_semana | Simulado | Miles de pasajeros/día por franja |
| perfil_latente | Simulado | Perfil con el que se generó la demanda (portal, centro, transbordo, intermedia). **No se usa para agrupar**, solo para validar |

`data/estaciones_clusters.csv` agrega el cluster asignado por K-Means y por el método jerárquico.

## 4. Metodología (cap. 16, técnicas de agrupamiento)
1. Estandarización de los 8 atributos (media 0, desviación 1), para que ninguno domine por su escala.
2. **K-Means** probado con k = 2 a 8. Se elige k con el método del codo y el coeficiente de silueta.
   Criterio: mayor silueta entre los k cuyo grupo más pequeño tenga al menos 3 estaciones. Sin esa
   restricción la silueta prefiere k = 6, que deja estaciones aisladas (Heroes y Calle146 en
   grupos de una sola estación), lo cual no sirve para segmentar.
3. **Agrupamiento jerárquico aglomerativo (Ward)** con el mismo k, para contrastar.
4. **PCA** a 2 componentes solo para visualizar.
5. Métricas: silueta, índice de Davies-Bouldin, y concordancia entre métodos (ARI).

## 5. Resultados (ver `docs/resultados_clustering.txt`)
Con k = 4 (silueta 0.635, Davies-Bouldin 0.578) aparecen cuatro grupos interpretables:
| Grupo | Estaciones | Rasgo principal |
|---|---|---|
| Portales | 6 (PortalUsme, PortalNorte, PortalSur, PortalSuba, Portal80, PortalAmericas) | Extremos de línea, lejos del centro, pico en la mañana |
| Centro | 8 | Cerca del centro, pico en la tarde |
| Nodos de transbordo | 5 (Heroes, Calle146, Ricaurte, SimonBolivar, AvenidaJimenez) | Varias líneas, alta intermediación y demanda alta todo el día |
| Intermedias | 14 | Baja demanda y poca conectividad |

K-Means y el jerárquico coinciden por completo (ARI = 1.0). Las figuras están en
`docs/fig_codo_silueta.png` y `docs/fig_clusters_pca.png`.

## 6. Limitaciones
- La demanda es simulada a partir de perfiles que se definieron antes, así que los grupos son
  fáciles de recuperar (ARI = 1.0 contra el perfil latente). Esto valida que el código funciona,
  pero **no** demuestra que existan esos grupos en la demanda real de TransMilenio.
- Son solo 33 estaciones, por lo que los resultados cambian si se modifica un solo grupo.
- Con datos reales basta reemplazar las columnas de demanda en `construir_dataset`.
