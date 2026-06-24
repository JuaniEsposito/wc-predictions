import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import numpy as np
import joblib
from datetime import datetime
import glob
from src.exceptions import ModelTrainingError, DataValidationError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def limpiar_modelos_antiguos(max_modelos=5):
    """
    Mantiene solo los max_modelos más recientes en /data
    Elimina los modelos antiguos para evitar acumulación
    """
    patron = os.path.join(DATA_DIR, 'modelo_*.pkl')
    modelos = glob.glob(patron)

    modelos.sort(key=os.path.getmtime, reverse=True)

    if len(modelos) > max_modelos:
        modelos_a_eliminar = modelos[max_modelos:]
        for modelo in modelos_a_eliminar:
            try:
                os.remove(modelo)
                print(f"   Eliminado modelo antiguo: {os.path.basename(modelo)}")
            except OSError as e:
                print(f"   ADVERTENCIA: No se pudo eliminar {modelo}: {e}")

    return len(modelos)

def guardar_modelo_con_versionado(modelo, tipo_modelo):
    """
    Guarda el modelo con timestamp y actualiza modelo_ganador.pkl
    """
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    nombre_versionado = f"modelo_{timestamp}.pkl"
    ruta_versionado = os.path.join(DATA_DIR, nombre_versionado)
    ruta_actual = os.path.join(DATA_DIR, 'modelo_ganador.pkl')

    joblib.dump(modelo, ruta_versionado)
    print(f"   Versión guardada: {nombre_versionado}")

    joblib.dump(modelo, ruta_actual)
    print(f"   Actualizado: modelo_ganador.pkl")

    total_modelos = limpiar_modelos_antiguos(max_modelos=5)
    print(f"   Total modelos en registry: {total_modelos}")

def entrenar():
    dataset_path = os.path.join(DATA_DIR, 'dataset_mundial.csv')
    if not os.path.exists(dataset_path):
        raise DataValidationError(
            f"No se encontró {dataset_path}. Ejecuta primero preparar_dataset.py"
        )

    df = pd.read_csv(dataset_path)
    print(f"Dataset cargado: {len(df)} registros")
    print(df.head())

    required_cols = ['xg_favor', 'xg_contra', 'equipo_encoded', 'oponente_encoded', 'victoria']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise DataValidationError(
            f"dataset_mundial.csv no tiene columnas requeridas: {missing}"
        )

    df['xg_diferencia'] = df['xg_favor'] - df['xg_contra']
    df['xg_ratio'] = df['xg_favor'] / (df['xg_contra'] + 0.01)
    df['xg_total'] = df['xg_favor'] + df['xg_contra']

    if 'importancia_partido' not in df.columns:
        df['importancia_partido'] = 1.0
    if 'dias_descanso' not in df.columns:
        df['dias_descanso'] = 7

    feature_cols = ['xg_favor', 'xg_contra', 'xg_diferencia', 'xg_ratio', 'xg_total',
                    'importancia_partido', 'dias_descanso', 'equipo_encoded', 'oponente_encoded']
    X = df[feature_cols]
    y = df['victoria']

    if len(y.unique()) < 2:
        raise ModelTrainingError(
            "El dataset solo tiene una clase (todas victorias o todas derrotas). "
            "Se necesitan datos con ambos resultados para entrenar."
        )

    if len(df) < 10:
        print("\nADVERTENCIA: Dataset muy pequeño. Usando todos los datos para entrenamiento.")
        X_train, X_test, y_train, y_test = X, X, y, y
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    acc_lr = 0
    log_reg = None
    try:
        log_reg = LogisticRegression(max_iter=500)
        log_reg.fit(X_train, y_train)
        pred_lr = log_reg.predict(X_test)
        acc_lr = accuracy_score(y_test, pred_lr)
        print(f"\nPrecisión Regresión Logística: {acc_lr:.2f}")
    except ValueError as e:
        print(f"\nADVERTENCIA: Regresión Logística no pudo entrenarse: {e}")

    acc_rf = 0
    rf_clf = None
    try:
        rf_clf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_clf.fit(X_train, y_train)
        pred_rf = rf_clf.predict(X_test)
        acc_rf = accuracy_score(y_test, pred_rf)
        print(f"Precisión Random Forest: {acc_rf:.2f}")
    except ValueError as e:
        print(f"ADVERTENCIA: Random Forest no pudo entrenarse: {e}")

    if acc_lr == 0 and acc_rf == 0:
        raise ModelTrainingError(
            "Ningún modelo pudo entrenarse. Revisa que el dataset tenga "
            "datos suficientes con victorias y derrotas."
        )

    print("\nResumen del Duelo de Modelos:")
    if acc_lr > acc_rf:
        print("Ganador: Regresión Logística")
    elif acc_rf > acc_lr:
        print("Ganador: Random Forest")
    else:
        print("Empate técnico")

    if acc_rf > 0 and rf_clf is not None:
        print("\nImportancia de Variables (Random Forest):")
        print("-" * 50)

        importancias = rf_clf.feature_importances_
        indices = np.argsort(importancias)[::-1]

        for i, idx in enumerate(indices):
            print(f"{i+1}. {feature_cols[idx]}: {importancias[idx]:.4f} ({importancias[idx]*100:.1f}%)")

        mas_importante = feature_cols[indices[0]]
        print(f"\nVariable más importante: {mas_importante}")

        if mas_importante in ['goles_favor', 'goles_contra']:
            print("   El rendimiento ofensivo/defensivo es el factor clave")
        elif mas_importante in ['equipo_encoded', 'oponente_encoded']:
            print("   La identidad del rival/equipo influye significativamente")

    if acc_lr >= acc_rf and acc_lr > 0 and log_reg is not None:
        print("\nGuardando modelo ganador (Regresión Logística)...")
        guardar_modelo_con_versionado(log_reg, "Regresión Logística")
        print("Modelo guardado exitosamente")
    elif acc_rf > acc_lr and acc_rf > 0 and rf_clf is not None:
        print("\nGuardando modelo ganador (Random Forest)...")
        guardar_modelo_con_versionado(rf_clf, "Random Forest")
        print("Modelo guardado exitosamente")

if __name__ == "__main__":
    entrenar()
