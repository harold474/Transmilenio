# -*- coding: utf-8 -*-
"""
rules_engine.py
----------------
Sistema experto (motor de reglas) con encadenamiento hacia adelante
(forward chaining), escrito en Python puro.

NOTA IMPORTANTE (léanla antes de sustentar el proyecto):
La primera versión de este archivo usaba la librería externa `experta`.
Esa librería no se actualiza desde 2021 y depende de partes del lenguaje
Python que fueron eliminadas en versiones recientes (3.10+), por lo que
falla al importarse en Python moderno (3.12, 3.13, 3.14...) sin importar
cuántos parches de compatibilidad se le agreguen.

En vez de pelear contra una dependencia externa rota, este archivo
implementa el MISMO PARADIGMA de sistema experto -motor de reglas de
encadenamiento hacia adelante, similar a CLIPS/Prolog- pero con una clase
propia (`MotorReglas`). Esto es exactamente lo que pide la actividad:
    - HECHOS representados como objetos (clases `Fact`).
    - REGLAS lógicas del tipo "SI se cumple un patrón ENTONCES se
      declara un nuevo hecho".
    - Un ciclo de inferencia que aplica las reglas hasta que no se
      puedan derivar más hechos nuevos (punto fijo).

La base de conocimiento sigue siendo:
    - Estacion(nombre=...)
    - Segmento(origen=..., destino=..., linea=..., minutos=...)

Y las reglas siguen derivando:
    1. Conexion(...): a partir de cada Segmento (regla 1 a 1).
    2. EstacionTransbordo(...): estaciones que aparecen en más de una
       línea (esto ya se calcula en knowledge_base.py y se declara aquí
       como hecho, igual que en la versión anterior).
"""

from knowledge_base import generar_segmentos, estaciones_por_linea


# ---------------------------------------------------------------------------
# 1. Representación de HECHOS (Facts)
# ---------------------------------------------------------------------------
class Fact(dict):
    """Un hecho es, simplemente, un diccionario con nombre de clase.
    Se accede a sus campos como en experta: hecho["origen"], hecho["linea"].
    """

    def __repr__(self):
        campos = ", ".join(f"{k}={v!r}" for k, v in self.items())
        return f"{type(self).__name__}({campos})"


class Estacion(Fact):
    """Hecho: una estación existe en la red.
    Campos obligatorios: nombre (str).
    """


class Segmento(Fact):
    """Hecho base: existe un tramo directo (sin transbordo) entre dos
    estaciones consecutivas de una misma línea troncal.
    Campos obligatorios: origen (str), destino (str), linea (str),
    minutos (int).
    """


class Conexion(Fact):
    """Hecho derivado: conexión utilizable para la búsqueda de ruta.
    Campos obligatorios: origen (str), destino (str), linea (str),
    minutos (int).
    """


class EstacionTransbordo(Fact):
    """Hecho derivado: la estación conecta dos o más líneas.
    Campos obligatorios: nombre (str), lineas (list).
    """


# ---------------------------------------------------------------------------
# 2. Motor de reglas (forward chaining)
# ---------------------------------------------------------------------------
class MotorReglas:
    """Motor de inferencia genérico de encadenamiento hacia adelante.

    - `declare(hecho)` agrega un hecho a la memoria de trabajo.
    - `regla(tipo_hecho)` es un decorador: registra una función que se
      debe ejecutar por cada hecho de ese tipo presente en la memoria.
    - `run()` aplica todas las reglas registradas sobre todos los hechos
      actuales, y repite el ciclo mientras se sigan derivando hechos
      nuevos (hasta llegar a un punto fijo, sin duplicar hechos ya
      conocidos). Esto es análogo al ciclo reconocer-actuar (RETE) de
      un sistema experto tipo CLIPS, simplificado para este ejercicio.
    """

    def __init__(self):
        self._reglas = []          # lista de (tipo_hecho, funcion)
        self.facts = []            # memoria de trabajo (lista de Fact)
        self._vistos = set()       # para evitar declarar hechos duplicados

    def regla(self, tipo_hecho):
        def decorador(funcion):
            self._reglas.append((tipo_hecho, funcion))
            return funcion
        return decorador

    def declare(self, hecho):
        # Se normaliza cada valor a algo "hasheable" (listas -> tuplas)
        # para poder usar el hecho como clave de deduplicación, sin
        # importar si algún campo es una lista (p. ej. EstacionTransbordo
        # guarda 'lineas' como lista).
        valores_normalizados = tuple(
            (k, tuple(v) if isinstance(v, list) else v)
            for k, v in sorted(hecho.items())
        )
        clave = (type(hecho).__name__, valores_normalizados)
        if clave in self._vistos:
            return False
        self._vistos.add(clave)
        self.facts.append(hecho)
        return True

    def run(self, max_ciclos=50):
        """Aplica las reglas repetidamente hasta que no se derive ningún
        hecho nuevo (punto fijo) o se alcance `max_ciclos` (salvaguarda
        contra reglas mal escritas que entrarían en bucle infinito)."""
        for _ in range(max_ciclos):
            hubo_hecho_nuevo = False
            # Se recorre una copia porque las reglas pueden agregar
            # hechos nuevos a self.facts mientras se itera.
            for hecho in list(self.facts):
                for tipo_hecho, funcion in self._reglas:
                    if isinstance(hecho, tipo_hecho):
                        antes = len(self.facts)
                        funcion(self, hecho)
                        if len(self.facts) != antes:
                            hubo_hecho_nuevo = True
            if not hubo_hecho_nuevo:
                break


class MotorTransMilenio(MotorReglas):
    """Motor de inferencia que construye el grafo de la red a partir de
    los segmentos declarados en la base de conocimiento."""

    def __init__(self):
        super().__init__()

        # Regla 1: "SI existe un Segmento(origen, destino, linea, minutos)
        # ENTONCES existe una Conexion utilizable por el algoritmo de
        # búsqueda". Es la regla lógica SI-ENTONCES central del sistema.
        @self.regla(Segmento)
        def derivar_conexion(motor, segmento):
            motor.declare(Conexion(
                origen=segmento["origen"],
                destino=segmento["destino"],
                linea=segmento["linea"],
                minutos=segmento["minutos"],
            ))

    def cargar_conocimiento(self):
        """Equivalente a @DefFacts de experta: carga los hechos
        iniciales (segmentos y estaciones) desde knowledge_base.py."""
        for origen, destino, linea, minutos in generar_segmentos():
            self.declare(Segmento(origen=origen, destino=destino,
                                   linea=linea, minutos=minutos))

        for estacion, lineas in estaciones_por_linea().items():
            self.declare(Estacion(nombre=estacion))
            if len(lineas) > 1:
                self.declare(EstacionTransbordo(nombre=estacion,
                                                 lineas=sorted(lineas)))

    def reset(self):
        """Reinicia la memoria de trabajo y vuelve a cargar los hechos
        iniciales (mismo nombre/comportamiento que experta.reset())."""
        self.facts = []
        self._vistos = set()
        self.cargar_conocimiento()

    def construir_grafo(self):
        """Ejecuta el motor y devuelve:
            grafo: dict estacion -> list[(vecino, linea, minutos)]
            transbordos: dict estacion -> list[lineas]
        """
        self.reset()
        self.run()

        grafo = {}
        transbordos = {}

        for hecho in self.facts:
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
