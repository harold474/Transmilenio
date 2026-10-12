# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, silhouette_score

from clustering import (ATRIBUTOS, MIN_ESTACIONES_GRUPO, agrupar,
                        construir_dataset, elegir_k, evaluar_k, preparar)
from knowledge_base import todas_las_estaciones


def test_dataset_una_fila_por_estacion_sin_nulos():
    df = construir_dataset()
    assert len(df) == len(todas_las_estaciones())
    assert df["estacion"].is_unique
    assert df[ATRIBUTOS].isna().sum().sum() == 0


def test_dataset_reproducible():
    pd.testing.assert_frame_equal(construir_dataset(), construir_dataset())


def test_transbordos_detectados_por_el_motor_de_reglas():
    df = construir_dataset().set_index("estacion")
    assert df.loc["Heroes", "num_lineas"] >= 2
    assert df.loc["Ricaurte", "num_lineas"] >= 2
    assert df.loc["PortalUsme", "num_lineas"] == 1


def test_estandarizacion_media_cero():
    X = preparar(construir_dataset())
    assert np.allclose(X.mean(axis=0), 0, atol=1e-9)
    assert np.allclose(X.std(axis=0), 1, atol=1e-9)


def test_k_elegido_no_deja_grupos_diminutos():
    tabla = evaluar_k(preparar(construir_dataset()))
    k = elegir_k(tabla)
    assert 2 <= k <= 8
    assert tabla.loc[tabla["k"] == k, "min_grupo"].iloc[0] >= MIN_ESTACIONES_GRUPO


def test_grupos_bien_separados_y_no_vacios():
    df = construir_dataset()
    X = preparar(df)
    k = elegir_k(evaluar_k(X))
    km, _ = agrupar(X, k)
    assert len(set(km.labels_)) == k
    assert silhouette_score(X, km.labels_) > 0.4


def test_kmeans_y_jerarquico_coinciden():
    X = preparar(construir_dataset())
    km, jer = agrupar(X, 4)
    assert adjusted_rand_score(km.labels_, jer.labels_) > 0.8


def test_clusters_recuperan_los_perfiles_simulados():
    df = construir_dataset()
    X = preparar(df)
    km, _ = agrupar(X, 4)
    assert adjusted_rand_score(df["perfil_latente"], km.labels_) > 0.8
