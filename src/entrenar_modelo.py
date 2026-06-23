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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def limpiar_modelos_antiguos(max_modelos=5):
    """
    Mantiene solo los max_modelos más recientes en /data
    Elimina los modelos antiguos para evitar acumulación
    """
    # Buscar todos los modelos con timestamp
    patron = os.path.join(DATA_DIR, 'modelo_*.pkl')
    modelos = glob.glob(patron)
    
    # Ordenar por fecha de modificación (más reciente primero)
    modelos.sort(key=os.path.getmtime, reverse=True)
    
    # Mantener solo los max_modelos más recientes
    if len(modelos) > max_modelos:
        modelos_a_eliminar = modelos[max_modelos:]
        for modelo in modelos_a_eliminar:
            try:
                os.remove(modelo)
                print(f"   🗑️  Eliminado modelo antiguo: {os.path.basename(modelo)}")
            except Exception as e:
                print(f"   ⚠️  Error eliminando {modelo}: {e}")
    
    return len(modelos)

def guardar_modelo_con_versionado(modelo, tipo_modelo):
    """
    Guarda el modelo con timestamp y actualiza modelo_ganador.pkl
    """
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    nombre_versionado = f"modelo_{timestamp}.pkl"
    ruta_versionado = os.path.join(DATA_DIR, nombre_versionado)
    ruta_actual = os.path.join(DATA_DIR, 'modelo_ganador.pkl')
    
    # Guardar versión con timestamp
    joblib.dump(modelo, ruta_versionado)
    print(f"   📦 Versión guardada: {nombre_versionado}")
    
    # Copiar a modelo_ganador.pkl para compatibilidad
    joblib.dump(modelo, ruta_actual)
    print(f"   🔄 Actualizado: modelo_ganador.pkl")
    
    # Limpiar modelos antiguos
    total_modelos = limpiar_modelos_antiguos(max_modelos=5)
    print(f"   📊 Total modelos en registry: {total_modelos}")

# 1. Cargar el dataset que generamos
df = pd.read_csv(os.path.join(DATA_DIR, 'dataset_mundial.csv'))

print(f"Dataset cargado: {len(df)} registros")
print(df.head())

# 2. Definir variables de entrada (X) y objetivo (y)
# Ahora usamos la potencia del xG en lugar de goles secos
# Agregamos features derivados de xG para aumentar su peso
df['xg_diferencia'] = df['xg_favor'] - df['xg_contra']
df['xg_ratio'] = df['xg_favor'] / (df['xg_contra'] + 0.01)  # Evitar división por cero
df['xg_total'] = df['xg_favor'] + df['xg_contra']

# Features elite: importancia y días de descanso
if 'importancia_partido' not in df.columns:
    df['importancia_partido'] = 1.0  # Default si no existe
if 'dias_descanso' not in df.columns:
    df['dias_descanso'] = 7  # Default si no existe

feature_cols = ['xg_favor', 'xg_contra', 'xg_diferencia', 'xg_ratio', 'xg_total', 
                'importancia_partido', 'dias_descanso', 'equipo_encoded', 'oponente_encoded']
X = df[feature_cols]
y = df['victoria']

# 3. Dividir en entrenamiento y prueba (80% entrenar, 20% testear)
# Si hay muy pocos datos, usar todos para entrenamiento
if len(df) < 10:
    print("\n⚠️  Dataset muy pequeño. Usando todos los datos para entrenamiento.")
    X_train, X_test, y_train, y_test = X, X, y, y
else:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Entrenar Regresión Logística
try:
    log_reg = LogisticRegression(max_iter=500)
    log_reg.fit(X_train, y_train)
    pred_lr = log_reg.predict(X_test)
    acc_lr = accuracy_score(y_test, pred_lr)
    print(f"\nPrecisión Regresión Logística: {acc_lr:.2f}")
except ValueError as e:
    print(f"\n⚠️  Regresión Logística no pudo entrenarse: {e}")
    print("   (Necesita al menos 2 clases en los datos)")
    acc_lr = 0

# 5. Entrenar Random Forest
try:
    rf_clf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_clf.fit(X_train, y_train)
    pred_rf = rf_clf.predict(X_test)
    acc_rf = accuracy_score(y_test, pred_rf)
    print(f"Precisión Random Forest: {acc_rf:.2f}")
except ValueError as e:
    print(f"⚠️  Random Forest no pudo entrenarse: {e}")
    acc_rf = 0

# 6. Comparar resultados
if acc_lr > 0 or acc_rf > 0:
    print("\n📊 Resumen del Duelo de Modelos:")
    if acc_lr > acc_rf:
        print("🏆 Ganador: Regresión Logística")
    elif acc_rf > acc_lr:
        print("🏆 Ganador: Random Forest")
    else:
        print("🤝 Empate técnico")
else:
    print("\n⚠️  No se pudo comparar modelos. Necesitas más datos con victorias y derrotas.")

# 7. Visualizar importancia de variables (Feature Importance)
if acc_rf > 0:
    print("\n🔍 Importancia de Variables (Random Forest):")
    print("-" * 50)
    
    importancias = rf_clf.feature_importances_
    indices = np.argsort(importancias)[::-1]
    
    for i, idx in enumerate(indices):
        print(f"{i+1}. {feature_cols[idx]}: {importancias[idx]:.4f} ({importancias[idx]*100:.1f}%)")
    
    # Identificar la variable más importante
    mas_importante = feature_cols[indices[0]]
    print(f"\n🎯 Variable más importante: {mas_importante}")
    
    if mas_importante in ['goles_favor', 'goles_contra']:
        print("   → El rendimiento ofensivo/defensivo es el factor clave")
    elif mas_importante in ['equipo_encoded', 'oponente_encoded']:
        print("   → La identidad del rival/equipo influye significativamente")

# 8. Guardar el modelo ganador para uso futuro (con versionado)
if acc_lr >= acc_rf and acc_lr > 0:
    print("\n💾 Guardando modelo ganador (Regresión Logística)...")
    guardar_modelo_con_versionado(log_reg, "Regresión Logística")
    print("✅ Modelo guardado exitosamente")
elif acc_rf > acc_lr and acc_rf > 0:
    print("\n💾 Guardando modelo ganador (Random Forest)...")
    guardar_modelo_con_versionado(rf_clf, "Random Forest")
    print("✅ Modelo guardado exitosamente")
else:
    print("\n⚠️  No se guardó ningún modelo (ninguno tuvo éxito)")
