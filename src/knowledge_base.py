# -*- coding: utf-8 -*-
"""
knowledge_base.py
------------------
Base de conocimiento del sistema de transporte masivo (inspirado en la
estructura troncal de TransMilenio - Bogotá).

IMPORTANTE (leer antes de sustentar):
Los nombres de portales/estaciones troncales son reales y conocidos,
pero el conjunto de estaciones intermedias, el orden exacto y sobre todo
los TIEMPOS DE VIAJE en minutos son DATOS APROXIMADOS/ILUSTRATIVOS creados
para poder construir y probar el sistema experto. Si su docente exige
datos oficiales exactos, pueden reemplazar esta información por datos
abiertos de TransMilenio (GTFS) sin cambiar el resto del código, ya que
todo el motor de reglas y de búsqueda trabaja a partir de esta estructura.

Cada línea (troncal) se define como una lista ordenada de estaciones.
Dos estaciones consecutivas de una misma línea están conectadas
directamente (sin transbordo). Una estación que aparece en más de una
línea es automáticamente una "estación de transbordo".
"""

# Coordenadas aproximadas (x, y) en km, solo para poder calcular una
# heurística de distancia en el algoritmo de búsqueda (A*). No representan
# coordenadas geográficas oficiales, únicamente una posición relativa
# consistente entre las estaciones.
COORDENADAS = {
    # Troncal Caracas (sur -> centro)
    "PortalUsme": (3.0, 0.0),
    "Molinos": (3.0, 2.0),
    "Consuelo": (3.0, 4.0),
    "CountrySur": (3.0, 6.0),
    "TercerMilenio": (3.0, 8.0),
    "AvenidaJimenez": (3.0, 10.0),
    "Heroes": (3.0, 12.0),

    # Troncal Autonorte (centro -> norte)
    "Calle72": (3.2, 14.0),
    "Calle85": (3.2, 16.0),
    "Calle100": (3.2, 18.0),
    "Calle106": (3.2, 19.5),
    "Calle146": (3.2, 22.0),
    "PortalNorte": (3.2, 25.0),

    # Troncal NQS (sur -> centro -> norte)
    "PortalSur": (0.0, 0.0),
    "Tunal": (0.5, 2.0),
    "Sena": (1.0, 4.0),
    "Ricaurte": (1.5, 8.0),
    "Alcala": (2.0, 16.0),

    # Troncal Suba
    "PortalSuba": (-4.0, 20.0),
    "SubaTV91": (-3.0, 18.0),
    "HumedalCordoba": (-2.0, 16.0),
    "MinutoDeDios": (-1.0, 14.0),
    "SimonBolivar": (0.0, 12.5),

    # Troncal Calle 80
    "Portal80": (-5.0, 22.0),
    "Boyaca": (-3.5, 18.0),
    "Quirigua": (-2.5, 16.0),
    "ElPolo": (-1.5, 14.5),

    # Troncal Américas
    "PortalAmericas": (-4.0, 4.0),
    "BibliotecaTintal": (-3.0, 5.0),
    "Banderas": (-2.0, 6.5),
    "Normandia": (-1.0, 7.5),

    # Eje Ambiental (alimentadora corta hacia el centro)
    "Universidades": (2.0, 11.0),
    "MuseoDelOro": (2.5, 10.5),
}

# Cada línea: lista ordenada de estaciones y lista de tiempos (minutos)
# entre estaciones consecutivas (longitud = num_estaciones - 1).
LINEAS = {
    "Caracas": {
        "estaciones": ["PortalUsme", "Molinos", "Consuelo", "CountrySur",
                        "TercerMilenio", "AvenidaJimenez", "Heroes"],
        "tiempos": [3, 3, 3, 3, 2, 3],
    },
    "Autonorte": {
        "estaciones": ["Heroes", "Calle72", "Calle85", "Calle100",
                        "Calle106", "Calle146", "PortalNorte"],
        "tiempos": [4, 3, 3, 2, 4, 5],
    },
    "NQS": {
        "estaciones": ["PortalSur", "Tunal", "Sena", "Ricaurte",
                        "Heroes", "Alcala", "Calle146"],
        "tiempos": [4, 3, 5, 4, 5, 4],
    },
    "Suba": {
        "estaciones": ["PortalSuba", "SubaTV91", "HumedalCordoba",
                        "MinutoDeDios", "SimonBolivar"],
        "tiempos": [3, 3, 3, 2],
    },
    "Calle80": {
        "estaciones": ["Portal80", "Boyaca", "Quirigua", "ElPolo",
                        "SimonBolivar", "Heroes"],
        "tiempos": [4, 3, 3, 2, 5],
    },
    "Americas": {
        "estaciones": ["PortalAmericas", "BibliotecaTintal", "Banderas",
                        "Normandia", "Ricaurte"],
        "tiempos": [3, 3, 3, 4],
    },
    "EjeAmbiental": {
        "estaciones": ["Universidades", "MuseoDelOro", "AvenidaJimenez"],
        "tiempos": [1, 1],
    },
}

# Penalización (en minutos) que representa el tiempo promedio de caminar
# y esperar el siguiente bus al hacer un transbordo entre líneas.
PENALIZACION_TRANSBORDO = 4


def generar_segmentos():
    """
    Construye la lista de segmentos (hechos base) a partir de LINEAS.
    Un segmento es una tupla: (origen, destino, linea, minutos)
    Se genera en ambos sentidos porque los buses circulan en las dos
    direcciones de la troncal.
    """
    segmentos = []
    for linea, datos in LINEAS.items():
        estaciones = datos["estaciones"]
        tiempos = datos["tiempos"]
        for i in range(len(estaciones) - 1):
            origen = estaciones[i]
            destino = estaciones[i + 1]
            minutos = tiempos[i]
            segmentos.append((origen, destino, linea, minutos))
            segmentos.append((destino, origen, linea, minutos))
    return segmentos


def estaciones_por_linea():
    """Devuelve un dict estacion -> set(lineas) para detectar transbordos."""
    mapa = {}
    for linea, datos in LINEAS.items():
        for est in datos["estaciones"]:
            mapa.setdefault(est, set()).add(linea)
    return mapa


def todas_las_estaciones():
    return sorted(COORDENADAS.keys())
