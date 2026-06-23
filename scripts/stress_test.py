#!/usr/bin/env python3
"""
Prueba de Stress con Partidos de Eliminación
Valida la precisión del modelo en partidos de alta importancia (importancia_partido >= 1.5)
"""

import pandas as pd
import joblib
import os
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Cargar dataset completo
df = pd.read_csv(os.path.join(DATA_DIR, 'dataset_mundial.csv'))

# Filtrar partidos de fase de eliminación (importancia_partido >= 1.5)
elimination_matches = df[df['importancia_partido'] >= 1.5].copy()

print("🏆 PRUEBA DE STRESS - PARTIDOS DE ELIMINACIÓN")
print("=" * 60)
print(f"Total partidos en dataset: {len(df)}")
print(f"Partidos de eliminación (importancia >= 1.5): {len(elimination_matches)}")

if len(elimination_matches) == 0:
    print("\n⚠️  No hay suficientes partidos de eliminación para la prueba")
    print("   El dataset necesita más partidos de alta importancia")
else:
    print(f"\n📊 Partidos de eliminación encontrados:")
    print(elimination_matches[['equipo', 'oponente', 'importancia_partido', 'dias_descanso', 'victoria']])
    
    # Cargar modelo y encoders
    modelo = joblib.load(os.path.join(DATA_DIR, 'modelo_ganador.pkl'))
    le_equipo = joblib.load(os.path.join(DATA_DIR, 'le_equipo.pkl'))
    le_oponente = joblib.load(os.path.join(DATA_DIR, 'le_oponente.pkl'))
    
    # Preparar features para predicción
    elimination_matches['xg_diferencia'] = elimination_matches['xg_favor'] - elimination_matches['xg_contra']
    elimination_matches['xg_ratio'] = elimination_matches['xg_favor'] / (elimination_matches['xg_contra'] + 0.01)
    elimination_matches['xg_total'] = elimination_matches['xg_favor'] + elimination_matches['xg_contra']
    
    feature_cols = ['xg_favor', 'xg_contra', 'xg_diferencia', 'xg_ratio', 'xg_total', 
                    'importancia_partido', 'dias_descanso', 'equipo_encoded', 'oponente_encoded']
    
    X_elim = elimination_matches[feature_cols]
    y_elim = elimination_matches['victoria']
    
    # Hacer predicciones
    pred_elim = modelo.predict(X_elim)
    
    # Calcular precisión
    acc_elim = accuracy_score(y_elim, pred_elim)
    
    print(f"\n🎯 RESULTADOS DE LA PRUEBA DE STRESS:")
    print(f"Precisión en partidos de eliminación: {acc_elim*100:.2f}%")
    
    if acc_elim >= 0.7:
        print("✅ EXCELENTE: Modelo mantiene alta precisión en partidos críticos")
    elif acc_elim >= 0.5:
        print("⚠️  ACEPTABLE: Modelo tiene precisión moderada en partidos críticos")
    else:
        print("❌ CRÍTICO: Modelo falla en partidos de alta importancia")
    
    # Reporte detallado
    print(f"\n📋 REPORTE DE CLASIFICACIÓN:")
    if len(y_elim.unique()) > 1:
        print(classification_report(y_elim, pred_elim, target_names=['Derrota', 'Victoria']))
    else:
        print("⚠️  Solo una clase en los datos de eliminación (todas victorias)")
        print(f"   Predicciones correctas: {sum(pred_elim == y_elim)}/{len(y_elim)}")
    
    # Análisis de errores
    errores = elimination_matches[pred_elim != y_elim]
    if len(errores) > 0:
        print(f"\n❌ ERRORES DEL MODELO ({len(errores)} partidos):")
        print(errores[['equipo', 'oponente', 'importancia_partido', 'victoria']].to_string(index=False))
    else:
        print(f"\n✅ SIN ERRORES: Predicción perfecta en partidos de eliminación")
