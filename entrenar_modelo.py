import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import numpy as np
import joblib

# 1. Cargar el dataset que generamos
df = pd.read_csv('dataset_mundial.csv')

print(f"Dataset cargado: {len(df)} registros")
print(df.head())

# 2. Definir variables de entrada (X) y objetivo (y)
# Ahora usamos la potencia del xG en lugar de goles secos
# Agregamos features derivados de xG para aumentar su peso
df['xg_diferencia'] = df['xg_favor'] - df['xg_contra']
df['xg_ratio'] = df['xg_favor'] / (df['xg_contra'] + 0.01)  # Evitar división por cero
df['xg_total'] = df['xg_favor'] + df['xg_contra']

feature_cols = ['xg_favor', 'xg_contra', 'xg_diferencia', 'xg_ratio', 'xg_total', 'equipo_encoded', 'oponente_encoded']
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
    log_reg = LogisticRegression()
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

# 8. Guardar el modelo ganador para uso futuro
if acc_lr >= acc_rf and acc_lr > 0:
    print("\n💾 Guardando modelo ganador (Regresión Logística)...")
    joblib.dump(log_reg, 'modelo_ganador.pkl')
    print("✅ Modelo guardado como modelo_ganador.pkl")
elif acc_rf > acc_lr and acc_rf > 0:
    print("\n💾 Guardando modelo ganador (Random Forest)...")
    joblib.dump(rf_clf, 'modelo_ganador.pkl')
    print("✅ Modelo guardado como modelo_ganador.pkl")
else:
    print("\n⚠️  No se guardó ningún modelo (ninguno tuvo éxito)")
