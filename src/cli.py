# -*- coding: utf-8 -*-
"""
cli.py
------
Punto de entrada del programa. Ejecutar con:

    python src/cli.py
    python src/cli.py --origen PortalSuba --destino PortalNorte
    python src/cli.py --listar

"""

import argparse
import sys

from knowledge_base import todas_las_estaciones
from rules_engine import obtener_grafo
from pathfinding import buscar_mejor_ruta


def imprimir_estaciones():
    print("Estaciones disponibles en la base de conocimiento:\n")
    for est in todas_las_estaciones():
        print(f"  - {est}")


def imprimir_ruta(resultado, origen, destino):
    if not resultado["encontrada"]:
        print(f"\nNo se encontró una ruta entre '{origen}' y '{destino}'.")
        return

    print(f"\nMejor ruta encontrada: {origen} -> {destino}")
    print(f"Tiempo total estimado: {resultado['minutos_totales']} minutos")
    print(f"Transbordos necesarios: {resultado['transbordos']}\n")

    linea_previa = None
    for i, paso in enumerate(resultado["pasos"], start=1):
        marca_transbordo = ""
        if linea_previa is not None and paso["linea"] != linea_previa:
            marca_transbordo = "  <-- TRANSBORDO"
        print(f"  {i}. {paso['desde']} -> {paso['hasta']}"
              f"  [Línea {paso['linea']}, {paso['minutos']} min]"
              f"{marca_transbordo}")
        linea_previa = paso["linea"]


def main():
    parser = argparse.ArgumentParser(
        description="Sistema experto de rutas para transporte masivo "
                    "(basado en reglas lógicas + búsqueda heurística A*)."
    )
    parser.add_argument("--origen", type=str, help="Estación de origen")
    parser.add_argument("--destino", type=str, help="Estación de destino")
    parser.add_argument("--listar", action="store_true",
                        help="Lista todas las estaciones disponibles")
    parser.add_argument("--sin-heuristica", action="store_true",
                        help="Ejecuta la búsqueda como Dijkstra puro "
                             "(sin heurística), útil para comparar en "
                             "el documento de pruebas.")
    args = parser.parse_args()

    if args.listar:
        imprimir_estaciones()
        return

    origen = args.origen
    destino = args.destino

    if not origen or not destino:
        imprimir_estaciones()
        origen = input("\nEstación de origen: ").strip()
        destino = input("Estación de destino: ").strip()

    print("\nCargando base de conocimiento y ejecutando el motor de "
          "reglas (experta)...")
    grafo, transbordos = obtener_grafo()
    print(f"Se derivaron {sum(len(v) for v in grafo.values())} conexiones "
          f"y se detectaron {len(transbordos)} estaciones de transbordo.")

    try:
        resultado = buscar_mejor_ruta(
            grafo, origen, destino,
            usar_heuristica=not args.sin_heuristica
        )
    except ValueError as e:
        print(f"\nError: {e}")
        sys.exit(1)

    imprimir_ruta(resultado, origen, destino)


if __name__ == "__main__":
    main()
