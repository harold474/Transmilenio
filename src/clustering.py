# -*- coding: utf-8 -*-
"""
clustering.py
-------------
Actividad 6 - Aprendizaje NO supervisado (técnicas de agrupamiento).

Problema: segmentar las estaciones de la red troncal en grupos con perfiles
parecidos (portales, estaciones del centro, nodos de transbordo, intermedias)
sin usar etiquetas previas. Las variables estructurales de cada estación
(número de líneas, grado, intermediación, distancia al centro) salen del
sistema experto (motor de reglas + A*); la demanda por franja es simulada.

Algoritmos (cap. 16 de Palma Méndez): K-Means y agrupamiento jerárquico
aglomerativo (Ward). Se elige k con codo + coeficiente de silueta y se
visualiza con PCA.

Uso:
    python src/clustering.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import matplotlib

matplotlib.use("Agg")  # sin ventana: solo guarda las imágenes
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (adjusted_rand_score, davies_bouldin_score,
                             silhouette_score)
from sklearn.preprocessing import StandardScaler

from knowledge_base import COORDENADAS, estaciones_por_linea, todas_las_estaciones
from pathfinding import buscar_mejor_ruta
from rules_engine import obtener_grafo

SEMILLA = 42
CENTRO = "AvenidaJimenez"   # referencia para la distancia al centro
RAIZ = os.path.join(os.path.dirname(__file__), "..")
RUTA_FEATURES = os.path.join(RAIZ, "data", "estaciones_features.csv")
RUTA_CLUSTERS = os.path.join(RAIZ, "data", "estaciones_clusters.csv")
RUTA_RESULTADOS = os.path.join(RAIZ, "docs", "resultados_clustering.txt")
RUTA_FIG_K = os.path.join(RAIZ, "docs", "fig_codo_silueta.png")
RUTA_FIG_PCA = os.path.join(RAIZ, "docs", "fig_clusters_pca.png")

ATRIBUTOS = ["num_lineas", "grado", "intermediacion", "dist_centro_km",
             "pico_am", "pico_pm", "valle", "fin_semana"]

# Demanda media (miles de pasajeros/día) por perfil latente y franja:
# (pico_am, pico_pm, valle, fin_semana). Solo sirve para simular los datos.
DEMANDA_PERFIL = {
    "portal":    (18.0, 5.0, 6.0, 7.0),    # sube mucha gente en la mañana
    "centro":    (7.0, 16.0, 10.0, 6.0),   # destino laboral: pico en la tarde
    "transbordo": (20.0, 20.0, 14.0, 11.0),  # alta demanda todo el día
    "intermedia": (5.0, 5.0, 3.5, 3.0),
}


def _perfil_latente(num_lineas, grado, dist_centro):
    if num_lineas >= 2:
        return "transbordo"
    if grado == 1 and dist_centro > 8:
        return "portal"
    if dist_centro <= 6:
        return "centro"
    return "intermedia"


def construir_dataset(semilla=SEMILLA):
    """Una fila por estación. Atributos estructurales a partir del sistema
    experto + demanda simulada por franja horaria."""
    rng = np.random.default_rng(semilla)
    grafo, _ = obtener_grafo()
    estaciones = todas_las_estaciones()
    lineas_de = estaciones_por_linea()

    # Intermediación: fracción de rutas óptimas (A*) entre todos los pares
    # de estaciones que pasan por la estación como parada intermedia.
    conteo = dict.fromkeys(estaciones, 0)
    total = 0
    for o in estaciones:
        for d in estaciones:
            if o == d:
                continue
            r = buscar_mejor_ruta(grafo, o, d)
            if not r["encontrada"]:
                continue
            total += 1
            for paso in r["pasos"][:-1]:
                conteo[paso["hasta"]] += 1

    cx, cy = COORDENADAS[CENTRO]
    filas = []
    for est in estaciones:
        x, y = COORDENADAS[est]
        dist = float(np.hypot(x - cx, y - cy))
        num_lineas = len(lineas_de[est])
        grado = len({v for v, _, _ in grafo.get(est, [])})
        perfil = _perfil_latente(num_lineas, grado, dist)
        media = np.array(DEMANDA_PERFIL[perfil])
        demanda = media * np.exp(rng.normal(0, 0.15, 4))
        filas.append({
            "estacion": est,
            "num_lineas": num_lineas,
            "grado": grado,
            "intermediacion": round(conteo[est] / total, 4),
            "dist_centro_km": round(dist, 2),
            "pico_am": round(float(demanda[0]), 2),
            "pico_pm": round(float(demanda[1]), 2),
            "valle": round(float(demanda[2]), 2),
            "fin_semana": round(float(demanda[3]), 2),
            "perfil_latente": perfil,   # solo para validar; NO se usa al agrupar
        })
    return pd.DataFrame(filas)


def preparar(df):
    """Estandariza los atributos (media 0, desviación 1)."""
    return StandardScaler().fit_transform(df[ATRIBUTOS].values)


def evaluar_k(X, k_min=2, k_max=8, semilla=SEMILLA):
    """Inercia (codo) y silueta de K-Means para cada k."""
    filas = []
    for k in range(k_min, k_max + 1):
        km = KMeans(n_clusters=k, n_init=20, random_state=semilla).fit(X)
        filas.append({"k": k, "inercia": km.inertia_,
                      "silueta": silhouette_score(X, km.labels_),
                      "min_grupo": int(np.bincount(km.labels_).min())})
    return pd.DataFrame(filas)


MIN_ESTACIONES_GRUPO = 3


def elegir_k(tabla_k, min_grupo=MIN_ESTACIONES_GRUPO):
    """k con mayor coeficiente de silueta entre los k cuyo grupo más pequeño
    tiene al menos `min_grupo` estaciones. Sin esta restricción la silueta
    prefiere k grandes que aíslan estaciones sueltas (grupos de 1), que no
    sirven para segmentar la red."""
    validos = tabla_k[tabla_k["min_grupo"] >= min_grupo]
    if validos.empty:
        validos = tabla_k
    return int(validos.loc[validos["silueta"].idxmax(), "k"])


def agrupar(X, k, semilla=SEMILLA):
    km = KMeans(n_clusters=k, n_init=20, random_state=semilla).fit(X)
    jer = AgglomerativeClustering(n_clusters=k, linkage="ward").fit(X)
    return km, jer


def nombrar_clusters(df, etiquetas):
    """Nombre interpretable de cada cluster según sus promedios."""
    nombres = {}
    for c in sorted(set(etiquetas)):
        sub = df[etiquetas == c]
        razon = sub["pico_am"].mean() / sub["pico_pm"].mean()
        if sub["num_lineas"].mean() >= 1.5:
            nombre = "Nodos de transbordo"
        elif razon > 1.5:
            nombre = "Portales (pico en la mañana)"
        elif razon < 0.8:
            nombre = "Centro (pico en la tarde)"
        else:
            nombre = "Estaciones intermedias"
        nombres[c] = f"C{c}: {nombre}"
    return nombres


def graficar_k(tabla_k, k_elegido, ruta):
    fig, ejes = plt.subplots(1, 2, figsize=(10, 4))
    ejes[0].plot(tabla_k["k"], tabla_k["inercia"], "o-")
    ejes[0].set(title="Método del codo", xlabel="k", ylabel="Inercia")
    ejes[1].plot(tabla_k["k"], tabla_k["silueta"], "o-", color="tab:green")
    ejes[1].axvline(k_elegido, color="gray", linestyle="--", label=f"k = {k_elegido}")
    ejes[1].set(title="Coeficiente de silueta", xlabel="k", ylabel="Silueta")
    ejes[1].legend()
    fig.tight_layout()
    fig.savefig(ruta, dpi=130)
    plt.close(fig)


def graficar_pca(X, df, etiquetas, nombres, ruta):
    pca = PCA(n_components=2, random_state=SEMILLA)
    Z = pca.fit_transform(X)
    fig, eje = plt.subplots(figsize=(10, 7))
    for c in sorted(set(etiquetas)):
        m = etiquetas == c
        eje.scatter(Z[m, 0], Z[m, 1], s=70, label=nombres[c])
    for i, est in enumerate(df["estacion"]):
        eje.annotate(est, (Z[i, 0], Z[i, 1]), fontsize=7,
                     xytext=(3, 3), textcoords="offset points")
    var = pca.explained_variance_ratio_
    eje.set(title="Estaciones agrupadas con K-Means (proyección PCA)",
            xlabel=f"Componente 1 ({var[0]:.0%} de la varianza)",
            ylabel=f"Componente 2 ({var[1]:.0%} de la varianza)")
    eje.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(ruta, dpi=130)
    plt.close(fig)
    return var


def main():
    os.makedirs(os.path.dirname(RUTA_FEATURES), exist_ok=True)
    df = construir_dataset()
    df.to_csv(RUTA_FEATURES, index=False)

    X = preparar(df)
    tabla_k = evaluar_k(X)
    k = elegir_k(tabla_k)
    km, jer = agrupar(X, k)

    et_km, et_jer = km.labels_, jer.labels_
    nombres = nombrar_clusters(df, et_km)
    df_res = df.copy()
    df_res["cluster_kmeans"] = et_km
    df_res["grupo"] = [nombres[c] for c in et_km]
    df_res["cluster_jerarquico"] = et_jer
    df_res.to_csv(RUTA_CLUSTERS, index=False)

    graficar_k(tabla_k, k, RUTA_FIG_K)
    var = graficar_pca(X, df, et_km, nombres, RUTA_FIG_PCA)

    centroides = df_res.groupby("grupo")[ATRIBUTOS].mean().round(2)
    tamanos = df_res["grupo"].value_counts().sort_index()
    composicion = pd.crosstab(df_res["grupo"], df_res["perfil_latente"])

    lineas = [
        f"Dataset: {len(df)} estaciones, {len(ATRIBUTOS)} atributos -> {os.path.normpath(RUTA_FEATURES)}",
        "",
        "Selección de k (K-Means):",
        tabla_k.round(3).to_string(index=False),
        f"k elegido (mayor silueta con grupos de al menos {MIN_ESTACIONES_GRUPO} estaciones): {k}",
        "",
        f"Silueta K-Means:           {silhouette_score(X, et_km):.3f}",
        f"Davies-Bouldin K-Means:    {davies_bouldin_score(X, et_km):.3f}  (menor es mejor)",
        f"Silueta jerárquico (Ward): {silhouette_score(X, et_jer):.3f}",
        f"ARI K-Means vs jerárquico: {adjusted_rand_score(et_km, et_jer):.3f}  (1 = idénticos)",
        f"ARI K-Means vs perfil latente (validación, dato simulado): "
        f"{adjusted_rand_score(df['perfil_latente'], et_km):.3f}",
        f"Varianza explicada por PCA (2 componentes): {var.sum():.1%}",
        "",
        "Tamaño de cada grupo:",
        tamanos.to_string(),
        "",
        "Promedio de atributos por grupo (centroides en unidades originales):",
        centroides.to_string(),
        "",
        "Composición de cada grupo según el perfil latente simulado:",
        composicion.to_string(),
        "",
        "Estaciones por grupo:",
    ]
    for g, sub in df_res.groupby("grupo"):
        lineas.append(f"  {g}: {', '.join(sub['estacion'])}")
    texto = "\n".join(lineas)
    print(texto)

    with open(RUTA_RESULTADOS, "w", encoding="utf-8") as f:
        f.write(texto + "\n")
    print(f"\nResultados en {os.path.normpath(RUTA_RESULTADOS)}")
    print(f"Figuras en {os.path.normpath(RUTA_FIG_K)} y {os.path.normpath(RUTA_FIG_PCA)}")


if __name__ == "__main__":
    main()
