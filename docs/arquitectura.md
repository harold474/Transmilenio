# Arquitectura del sistema (guion de apoyo para el video)

## 1. Representación del conocimiento (lógica de reglas)

- **Hechos base**: cada tramo directo entre dos estaciones consecutivas
  de una misma línea troncal es un hecho `Segmento(origen, destino,
  linea, minutos)`.
- **Regla de inferencia**: "si existe un `Segmento` entre A y B en la
  línea L con tiempo M, entonces existe una `Conexion` utilizable entre
  A y B". Esto es una regla lógica de tipo `SI ... ENTONCES ...`,
  implementada con un motor de encadenamiento hacia adelante propio
  (`MotorReglas` en `rules_engine.py`), similar en su lógica a
  CLIPS/Prolog: hechos en una memoria de trabajo, reglas que se
  disparan cuando aparece un hecho del tipo que les interesa, y un
  ciclo que se repite hasta que no se derivan hechos nuevos (punto
  fijo).
- **Regla derivada de transbordo**: "si una estación pertenece a más de
  una línea, entonces es una estación de transbordo".

## 2. Búsqueda de la mejor ruta

- Sobre el grafo derivado por el motor de reglas se aplica **A\***, un
  algoritmo de búsqueda heurística vista en la unidad de técnicas de
  búsqueda.
- El **costo** de moverse de una estación a otra es el tiempo en
  minutos del tramo, más una **penalización fija** si esa conexión
  implica cambiar de línea (transbordo).
- La **heurística** es la distancia en línea recta hasta el destino,
  dividida por una velocidad optimista. Esto hace que A* explore
  primero los caminos "en la dirección correcta", sin perder la
  garantía de encontrar la ruta óptima (la heurística nunca
  sobreestima el costo real).

## 3. Por qué esto cumple con la actividad

- Usa **representación del conocimiento en reglas lógicas** (capítulo 2
  y 3 de Benítez): hechos + reglas SI-ENTONCES con un motor de
  inferencia de encadenamiento hacia adelante propio.
- Usa **técnicas de búsqueda heurística** (capítulo 9): A* con función
  heurística admisible.
- Resuelve un problema real y acotado: la mejor ruta entre dos puntos
  del sistema de transporte masivo.

## 4. Ideas para mencionar en el video

1. Mostrar `knowledge_base.py` y explicar cómo se representa una línea
   troncal como una secuencia de estaciones.
2. Mostrar `rules_engine.py` y explicar la regla que convierte
   segmentos en conexiones, y cómo se detectan los transbordos.
3. Ejecutar `python src/cli.py --origen ... --destino ...` en vivo y
   explicar la salida (tiempo total, transbordos, paso a paso).
4. Mostrar `pytest -v` corriendo y pasando.
5. Mostrar el repositorio en GitHub con los commits de cada integrante.
