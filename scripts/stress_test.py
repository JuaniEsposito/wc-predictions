#!/usr/bin/env python3
"""
Prueba de Stress con Partidos de Eliminación
Valida la precisión del modelo en partidos de alta importancia (importancia_partido >= 1.5)
"""

import pandas as pd
import joblib
import os
import sys
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')


def run_stress_test():
    dataset_path = os.path.join(DATA_DIR, 'dataset_mundial.csv')
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"No se encontró {dataset_path}. Ejecuta primero el pipeline.")
    df = pd.read_csv(dataset_path)

    elimination_matches = df[df['importancia_partido'] >= 1.5].copy()

    print("PRUEBA DE STRESS - PARTIDOS DE ELIMINACION")
    print("=" * 60)
    print(f"Total partidos en dataset: {len(df)}")
    print(f"Partidos de eliminacion (importancia >= 1.5): {len(elimination_matches)}")

    if len(elimination_matches) == 0:
        print("\nNo hay suficientes partidos de eliminacion para la prueba")
        return

    print(f"\nPartidos de eliminacion encontrados:")
    print(elimination_matches[['equipo', 'oponente', 'importancia_partido', 'dias_descanso', 'victoria']])

    for name in ['modelo_ganador.pkl', 'le_equipo.pkl', 'le_oponente.pkl']:
        path = os.path.join(DATA_DIR, name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"No se encontró {path}. Ejecuta primero entrenar_modelo.py")

    modelo = joblib.load(os.path.join(DATA_DIR, 'modelo_ganador.pkl'))
    le_equipo = joblib.load(os.path.join(DATA_DIR, 'le_equipo.pkl'))
    le_oponente = joblib.load(os.path.join(DATA_DIR, 'le_oponente.pkl'))

    elimination_matches['xg_diferencia'] = elimination_matches['xg_favor'] - elimination_matches['xg_contra']
    elimination_matches['xg_ratio'] = elimination_matches['xg_favor'] / (elimination_matches['xg_contra'] + 0.01)
    elimination_matches['xg_total'] = elimination_matches['xg_favor'] + elimination_matches['xg_contra']

    feature_cols = ['xg_favor', 'xg_contra', 'xg_diferencia', 'xg_ratio', 'xg_total',
                    'importancia_partido', 'dias_descanso', 'equipo_encoded', 'oponente_encoded']

    X_elim = elimination_matches[feature_cols]
    y_elim = elimination_matches['victoria']

    pred_elim = modelo.predict(X_elim)
    acc_elim = accuracy_score(y_elim, pred_elim)

    print(f"\nRESULTADOS DE LA PRUEBA DE STRESS:")
    print(f"Precision en partidos de eliminacion: {acc_elim*100:.2f}%")

    if len(y_elim.unique()) > 1:
        print(classification_report(y_elim, pred_elim, target_names=['Derrota', 'Victoria']))

    errores = elimination_matches[pred_elim != y_elim]
    if len(errores) > 0:
        print(f"\nERRORES DEL MODELO ({len(errores)} partidos):")
        print(errores[['equipo', 'oponente', 'importancia_partido', 'victoria']].to_string(index=False))


if __name__ == "__main__":
    run_stress_test()
