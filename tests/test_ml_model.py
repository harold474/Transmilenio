# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pandas as pd
from sklearn.model_selection import train_test_split

from ml_model import entrenar, generar_dataset, preparar


def test_dataset_forma_y_etiquetas():
    df = generar_dataset(300)
    assert len(df) == 300
    assert set(df["ocupacion"].unique()) <= {"baja", "media", "alta"}
    assert df.isna().sum().sum() == 0


def test_dataset_reproducible():
    pd.testing.assert_frame_equal(generar_dataset(100), generar_dataset(100))


def test_atributos_vienen_del_sistema_experto():
    df = generar_dataset(300)
    assert (df["num_transbordos"] >= 0).all()
    assert (df["minutos_base"] > 0).all()
    assert (df["origen"] != df["destino"]).all()


def test_modelo_supera_baseline():
    df = generar_dataset(2000)
    X, y = preparar(df)
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)
    modelo = entrenar(X_tr, y_tr)
    baseline = y_te.value_counts(normalize=True).max()
    assert modelo.score(X_te, y_te) > baseline + 0.10
