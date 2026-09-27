# -*- coding: utf-8 -*-
"""
rules_engine.py
----------------
Sistema experto (motor de reglas) construido con la librería `experta`.

La idea del ejercicio es representar el conocimiento del sistema de
transporte como HECHOS (facts):
    - Estacion(nombre=...)
    - Segmento(origen=..., destino=..., linea=..., minutos=...)

Y usar REGLAS para:
    1. Detectar cuáles estaciones son puntos de transbordo (aparecen en
       más de una línea).
    2. Derivar, a partir de los segmentos, los hechos de "Conexion" que
       usará luego el algoritmo de búsqueda (grafo ponderado).

NOTA DE COMPATIBILIDAD:
`experta` fue escrito para versiones antiguas de Python y usa
`collections.Mapping`, que fue removido de la librería estándar en
Python 3.10. El parche de abajo restaura ese alias antes de importar
experta, para que la librería funcione en Python 3.10+.
"""

import collections
import collections.abc

# --- Parche de compatibilidad para Python 3.10+ ---------------------------
if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping
if not hasattr(collections, "MutableMapping"):
    collections.MutableMapping = collections.abc.MutableMapping
if not hasattr(collections, "Sequence"):
    collections.Sequence = collections.abc.Sequence
# ---------------------------------------------------------------------------

from experta import KnowledgeEngine, Fact, Field, Rule, MATCH, DefFacts

from knowledge_base import generar_segmentos, estaciones_por_linea


class Estacion(Fact):
    """Hecho: una estación existe en la red."""
    nombre = Field(str, mandatory=True)


class Segmento(Fact):
    """Hecho base: existe un tramo directo (sin transbordo) entre dos
    estaciones consecutivas de una misma línea troncal."""
    origen = Field(str, mandatory=True)
    destino = Field(str, mandatory=True)
    linea = Field(str, mandatory=True)
    minutos = Field(int, mandatory=True)


class Conexion(Fact):
    """Hecho derivado: conexión utilizable para la búsqueda de ruta."""
    origen = Field(str, mandatory=True)
    destino = Field(str, mandatory=True)
    linea = Field(str, mandatory=True)
    minutos = Field(int, mandatory=True)


class EstacionTransbordo(Fact):
    """Hecho derivado: la estación conecta dos o más líneas."""
    nombre = Field(str, mandatory=True)
    lineas = Field(list, mandatory=True)


class MotorTransMilenio(KnowledgeEngine):
    """Motor de inferencia que construye el grafo de la red a partir de
    los segmentos declarados en la base de conocimiento."""

    @DefFacts()
    def cargar_conocimiento(self):
        """Se ejecuta automáticamente al hacer reset(): carga los hechos
        iniciales (segmentos y estaciones) desde knowledge_base.py."""
        for origen, destino, linea, minutos in generar_segmentos():
            yield Segmento(origen=origen, destino=destino,
                            linea=linea, minutos=minutos)

        for estacion, lineas in estaciones_por_linea().items():
            yield Estacion(nombre=estacion)
            if len(lineas) > 1:
                yield EstacionTransbordo(nombre=estacion,
                                          lineas=sorted(lineas))

    # Regla 1: todo segmento válido se convierte en una conexión
    # utilizable por el algoritmo de búsqueda.
    @Rule(Segmento(origen=MATCH.o, destino=MATCH.d,
                    linea=MATCH.l, minutos=MATCH.m))
    def derivar_conexion(self, o, d, l, m):
        self.declare(Conexion(origen=o, destino=d, linea=l, minutos=m))

    def construir_grafo(self):
        """Ejecuta el motor y devuelve:
            grafo: dict estacion -> list[(vecino, linea, minutos)]
            transbordos: dict estacion -> list[lineas]
        """
        self.reset()
        self.run()

        grafo = {}
        transbordos = {}

        for hecho in self.facts.values():
            if isinstance(hecho, Conexion):
                grafo.setdefault(hecho["origen"], []).append(
                    (hecho["destino"], hecho["linea"], hecho["minutos"])
                )
            elif isinstance(hecho, EstacionTransbordo):
                transbordos[hecho["nombre"]] = hecho["lineas"]

        return grafo, transbordos


def obtener_grafo():
    """Función de conveniencia usada por el resto del proyecto."""
    motor = MotorTransMilenio()
    return motor.construir_grafo()
