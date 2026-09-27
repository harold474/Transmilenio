# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from rules_engine import obtener_grafo


def test_grafo_no_vacio():
    grafo, transbordos = obtener_grafo()
    assert len(grafo) > 0


def test_conexion_bidireccional_misma_linea():
    grafo, _ = obtener_grafo()
    # Molinos y Consuelo son consecutivas en la línea Caracas
    destinos_desde_molinos = [v[0] for v in grafo["Molinos"]]
    destinos_desde_consuelo = [v[0] for v in grafo["Consuelo"]]
    assert "Consuelo" in destinos_desde_molinos
    assert "Molinos" in destinos_desde_consuelo


def test_heroes_es_transbordo():
    _, transbordos = obtener_grafo()
    assert "Heroes" in transbordos
    assert len(transbordos["Heroes"]) >= 2


def test_ricaurte_es_transbordo():
    _, transbordos = obtener_grafo()
    assert "Ricaurte" in transbordos
