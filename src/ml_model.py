# -*- coding: utf-8 -*-
"""
ml_model.py
-----------
Actividad 5 - Aprendizaje supervisado (árboles de decisión).

Problema: predecir el NIVEL DE OCUPACIÓN (baja / media / alta) de un viaje
en la red troncal. Cada fila del dataset es un viaje cuya ruta fue calculada
por el sistema experto de la actividad anterior (motor de reglas + A*), de
modo que los atributos de la ruta (minutos base, estaciones, transbordos,
estaciones de transbordo atravesadas) salen directamente de ese sistema.

Uso:
    python src/ml_model.py
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text

from knowledge_base import todas_las_estaciones
from pathfinding import buscar_mejor_ruta
from rules_engine import obtener_grafo

SEMILLA = 42
RAIZ = os.path.join(os.path.dirname(__file__), "..")
RUTA_CSV = os.path.join(RAIZ, "data", "viajes_transmilenio.csv")
RUTA_REGLAS = os.path.join(RAIZ, "docs", "reglas_arbol.txt")
RUTA_RESULTADOS = os.path.join(RAIZ, "docs", "resultados_modelo.txt")


def _es_hora_pico(hora):
    return (6 <= hora <= 9) or (17 <= hora <= 19)


def generar_dataset(n=3000, semilla=SEMILLA):
    """Genera n viajes. El origen/destino se eligen al azar, la ruta la
    calcula A* sobre el grafo del motor de reglas, y el contexto (hora, día,
    lluvia, festivo) se simula. La etiqueta `ocupacion` se genera con un
    modelo de demanda con ruido (datos sintéticos)."""
    rng = np.random.default_rng(semilla)
    azar = random.Random(semilla)
    grafo, transbordos = obtener_grafo()
    estaciones = todas_las_estaciones()

    # Se calcula cada ruta una sola vez (33*32 pares) y se reutiliza.
    rutas = {}
    for o in estaciones:
        for d in estaciones:
            if o != d:
                r = buscar_mejor_ruta(grafo, o, d)
                if r["encontrada"]:
                    rutas[(o, d)] = r
    pares = list(rutas.keys())

    filas = []
    for _ in range(n):
        o, d = azar.choice(pares)
        r = rutas[(o, d)]
        pasos = r["pasos"]
        intermedias = [p["hasta"] for p in pasos[:-1]]
        n_transb_atravesadas = sum(1 for e in intermedias if e in transbordos)

        hora = int(rng.integers(4, 23))
        dia = int(rng.integers(0, 7))                 # 0 = lunes ... 6 = domingo
        festivo = int(rng.random() < 0.05)
        lluvia = int(rng.random() < 0.25)
        habil = dia < 5 and festivo == 0

        puntaje = (
            2.0 * (habil and _es_hora_pico(hora))
            + 0.8 * lluvia
            + 0.45 * r["transbordos"]
            + 0.30 * n_transb_atravesadas
            + 0.03 * len(pasos)
            - 1.0 * (dia == 6 or festivo == 1)
            - 0.8 * (hora < 6 or hora > 20)
            + rng.normal(0, 0.45)
        )
        if puntaje < 0.9:
            ocupacion = "baja"
        elif puntaje < 2.2:
            ocupacion = "media"
        else:
            ocupacion = "alta"

        filas.append({
            "origen": o,
            "destino": d,
            "hora": hora,
            "dia_semana": dia,
            "es_festivo": festivo,
            "lluvia": lluvia,
            "linea_inicial": pasos[0]["linea"],
            "minutos_base": r["minutos_totales"],
            "num_estaciones": len(pasos),
            "num_transbordos": r["transbordos"],
            "transbordos_atravesados": n_transb_atravesadas,
            "ocupacion": ocupacion,
        })
    return pd.DataFrame(filas)


def preparar(df):
    """Devuelve (X, y). Agrega atributos derivados y codifica la línea."""
    df = df.copy()
    df["es_habil"] = ((df["dia_semana"] < 5) & (df["es_festivo"] == 0)).astype(int)
    df["es_hora_pico"] = df["hora"].apply(lambda h: int(_es_hora_pico(h)))
    X = df.drop(columns=["ocupacion", "origen", "destino"])
    X = pd.get_dummies(X, columns=["linea_inicial"])
    return X, df["ocupacion"]


def entrenar(X_tr, y_tr):
    modelo = DecisionTreeClassifier(
        criterion="entropy", max_depth=6, min_samples_leaf=15,
        class_weight="balanced", random_state=SEMILLA,
    )
    return modelo.fit(X_tr, y_tr)


def main():
    os.makedirs(os.path.dirname(RUTA_CSV), exist_ok=True)
    df = generar_dataset()
    df.to_csv(RUTA_CSV, index=False)

    X, y = preparar(df)
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=SEMILLA, stratify=y)
    modelo = entrenar(X_tr, y_tr)
    pred = modelo.predict(X_te)
    etiquetas = ["baja", "media", "alta"]

    baseline = y_te.value_counts(normalize=True).max()
    cv = cross_val_score(entrenar(X, y), X, y, cv=5)
    imp = pd.Series(modelo.feature_importances_, index=X.columns)

    lineas = [
        f"Dataset: {len(df)} filas -> {os.path.normpath(RUTA_CSV)}",
        "Distribución de la clase objetivo:",
        df["ocupacion"].value_counts().to_string(),
        "",
        f"Baseline (clase mayoritaria): {baseline:.3f}",
        f"Exactitud entrenamiento:      {modelo.score(X_tr, y_tr):.3f}",
        f"Exactitud prueba:             {modelo.score(X_te, y_te):.3f}",
        f"Validación cruzada (5):       {cv.mean():.3f} +/- {cv.std():.3f}",
        "",
        "Matriz de confusión (filas = real, columnas = predicho):",
        pd.DataFrame(confusion_matrix(y_te, pred, labels=etiquetas),
                     index=etiquetas, columns=etiquetas).to_string(),
        "",
        classification_report(y_te, pred, labels=etiquetas),
        "Importancia de atributos (top 6):",
        imp.sort_values(ascending=False).head(6).round(3).to_string(),
    ]
    texto = "\n".join(lineas)
    print(texto)

    with open(RUTA_RESULTADOS, "w", encoding="utf-8") as f:
        f.write(texto + "\n")
    with open(RUTA_REGLAS, "w", encoding="utf-8") as f:
        f.write(export_text(modelo, feature_names=list(X.columns)))
    print(f"\nResultados en {os.path.normpath(RUTA_RESULTADOS)}")
    print(f"Reglas del árbol en {os.path.normpath(RUTA_REGLAS)}")


if __name__ == "__main__":
    main()
