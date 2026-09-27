# -*- coding: utf-8 -*-
"""
pathfinding.py
---------------
Búsqueda heurística (A*) sobre el grafo derivado por el motor de reglas.

El "estado" de búsqueda no es solo la estación actual, sino el par
(estacion, linea_actual), porque el costo real de moverse depende de si
hay que hacer transbordo (cambiar de línea) o no. Esto es lo que permite
que el algoritmo prefiera rutas con menos transbordos cuando el tiempo
total es similar.

Heurística admisible: distancia en línea recta entre la estación actual
y el destino, dividida por una velocidad optimista (asumimos que en el
mejor de los casos el bus avanza a 45 km/h en línea recta). Esto nunca
sobreestima el tiempo real restante, por lo que A* sigue siendo óptimo.
"""

import heapq
import math

from knowledge_base import COORDENADAS, PENALIZACION_TRANSBORDO


VELOCIDAD_OPTIMISTA_KMH = 45.0


def _distancia_km(a, b):
    (x1, y1) = COORDENADAS[a]
    (x2, y2) = COORDENADAS[b]
    return math.dist((x1, y1), (x2, y2))


def heuristica(estacion, destino):
    dist_km = _distancia_km(estacion, destino)
    minutos_optimistas = (dist_km / VELOCIDAD_OPTIMISTA_KMH) * 60.0
    return minutos_optimistas


def buscar_mejor_ruta(grafo, origen, destino, usar_heuristica=True):
    """
    Devuelve un dict con:
        encontrada: bool
        minutos_totales: float
        transbordos: int
        pasos: lista de dicts {desde, hasta, linea, minutos}
    o None si no existe ruta.
    """
    if origen not in grafo and origen not in COORDENADAS:
        raise ValueError(f"Estación de origen desconocida: {origen}")
    if destino not in COORDENADAS:
        raise ValueError(f"Estación de destino desconocida: {destino}")

    # Estado = (estacion, linea_actual). linea_actual=None al iniciar.
    estado_inicial = (origen, None)

    costo_g = {estado_inicial: 0.0}
    padres = {}  # estado -> (estado_previo, linea_usada, minutos_tramo)

    h0 = heuristica(origen, destino) if usar_heuristica else 0.0
    frontera = [(h0, 0.0, estado_inicial)]
    visitados = set()

    while frontera:
        _, g_actual, estado = heapq.heappop(frontera)
        if estado in visitados:
            continue
        visitados.add(estado)

        estacion_actual, linea_actual = estado

        if estacion_actual == destino:
            return _reconstruir_resultado(padres, estado, g_actual)

        for vecino, linea_tramo, minutos in grafo.get(estacion_actual, []):
            costo_extra = minutos
            if linea_actual is not None and linea_tramo != linea_actual:
                costo_extra += PENALIZACION_TRANSBORDO

            nuevo_g = g_actual + costo_extra
            nuevo_estado = (vecino, linea_tramo)

            if nuevo_estado in visitados:
                continue

            if nuevo_g < costo_g.get(nuevo_estado, math.inf):
                costo_g[nuevo_estado] = nuevo_g
                padres[nuevo_estado] = (estado, linea_tramo, minutos)
                h = heuristica(vecino, destino) if usar_heuristica else 0.0
                heapq.heappush(frontera, (nuevo_g + h, nuevo_g, nuevo_estado))

    return {"encontrada": False, "minutos_totales": None,
            "transbordos": None, "pasos": []}


def _reconstruir_resultado(padres, estado_final, minutos_totales):
    pasos = []
    estado = estado_final
    while estado in padres:
        estado_previo, linea_usada, minutos_tramo = padres[estado]
        pasos.append({
            "desde": estado_previo[0],
            "hasta": estado[0],
            "linea": linea_usada,
            "minutos": minutos_tramo,
        })
        estado = estado_previo
    pasos.reverse()

    lineas_usadas = [p["linea"] for p in pasos]
    transbordos = 0
    for i in range(1, len(lineas_usadas)):
        if lineas_usadas[i] != lineas_usadas[i - 1]:
            transbordos += 1

    return {
        "encontrada": True,
        "minutos_totales": round(minutos_totales, 1),
        "transbordos": transbordos,
        "pasos": pasos,
    }
