# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from rules_engine import obtener_grafo
from pathfinding import buscar_mejor_ruta


def test_ruta_directa_misma_linea_sin_transbordo():
    grafo, _ = obtener_grafo()
    resultado = buscar_mejor_ruta(grafo, "PortalUsme", "Heroes")
    assert resultado["encontrada"] is True
    assert resultado["transbordos"] == 0


def test_ruta_con_transbordo_obligatorio():
    grafo, _ = obtener_grafo()
    # PortalSuba (línea Suba) a PortalAmericas (línea Americas)
    # obliga a pasar por SimonBolivar/Heroes/Ricaurte -> requiere transbordos
    resultado = buscar_mejor_ruta(grafo, "PortalSuba", "PortalAmericas")
    assert resultado["encontrada"] is True
    assert resultado["transbordos"] >= 1


def test_estacion_inexistente_lanza_error():
    grafo, _ = obtener_grafo()
    try:
        buscar_mejor_ruta(grafo, "EstacionQueNoExiste", "Heroes")
        assert False, "Debió lanzar ValueError"
    except ValueError:
        pass


def test_heuristica_y_dijkstra_dan_mismo_tiempo_total():
    grafo, _ = obtener_grafo()
    r1 = buscar_mejor_ruta(grafo, "PortalNorte", "PortalSur",
                            usar_heuristica=True)
    r2 = buscar_mejor_ruta(grafo, "PortalNorte", "PortalSur",
                            usar_heuristica=False)
    assert r1["minutos_totales"] == r2["minutos_totales"]
