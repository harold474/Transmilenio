# Documento de Pruebas — Sistema Experto de Rutas TransMilenio

> Instrucciones: completen las columnas "Resultado obtenido" y
> "¿Pasó?" ejecutando realmente el programa (`python src/cli.py ...`)
> y peguen una captura de pantalla de cada caso. Al final, exporten
> este archivo a PDF (por ejemplo desde VS Code, Typora, o
> `pandoc plan_pruebas.md -o plan_pruebas.pdf`).

## 1. Datos del equipo

- Integrantes: ____________________
- Repositorio: ____________________
- Fecha: ____________________

## 2. Casos de prueba manuales

| # | Origen | Destino | Resultado esperado | Resultado obtenido | ¿Pasó? |
|---|--------|---------|---------------------|---------------------|--------|
| 1 | PortalUsme | Heroes | Ruta directa por línea Caracas, 0 transbordos | | |
| 2 | PortalSuba | PortalNorte | Ruta con al menos 2 transbordos | | |
| 3 | PortalSur | PortalAmericas | Ruta con al menos 1 transbordo (vía Ricaurte) | | |
| 4 | Universidades | AvenidaJimenez | Ruta corta por Eje Ambiental | | |
| 5 | EstacionInexistente | Heroes | El programa debe mostrar un error controlado | | |

## 3. Pruebas automatizadas (pytest)

Ejecutar:

```bash
pytest -v
```

Pegar aquí la captura de consola con el resumen final (`X passed`):

```
(pegar salida de pytest)
```

## 4. Comparación heurística vs. sin heurística

Ejecutar el mismo trayecto con y sin heurística para verificar que el
tiempo total encontrado es el mismo (la heurística solo acelera la
búsqueda, no debería cambiar el resultado óptimo):

```bash
python src/cli.py --origen PortalNorte --destino PortalSur
python src/cli.py --origen PortalNorte --destino PortalSur --sin-heuristica
```

| Método | Tiempo total (min) | Transbordos |
|--------|---------------------|--------------|
| Con heurística (A*) | | |
| Sin heurística (Dijkstra) | | |

## 5. Conclusiones

(Escribir 2-3 párrafos: qué tan bien funcionó el sistema de reglas, qué
limitaciones tiene el modelo de datos, y qué mejorarían con más tiempo,
por ejemplo usar datos oficiales GTFS de TransMilenio o agregar
horarios reales por franja horaria.)
