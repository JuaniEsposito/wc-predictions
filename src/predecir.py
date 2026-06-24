import sys
import os
import pandas as pd
import joblib
import json
from src.exceptions import PredictionError, ConfigurationError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def predecir(equipo, oponente, importancia_partido=1.0, dias_descanso=7):
    modelo_path = os.path.join(DATA_DIR, 'modelo_ganador.pkl')
    le_equipo_path = os.path.join(DATA_DIR, 'le_equipo.pkl')
    le_oponente_path = os.path.join(DATA_DIR, 'le_oponente.pkl')

    for path, name in [(modelo_path, "modelo_ganador.pkl"),
                       (le_equipo_path, "le_equipo.pkl"),
                       (le_oponente_path, "le_oponente.pkl")]:
        if not os.path.exists(path):
            raise ConfigurationError(
                f"No se encontró {name} en {DATA_DIR}. "
                "Ejecuta primero entrenar_modelo.py"
            )

    modelo = joblib.load(modelo_path)
    le_equipo = joblib.load(le_equipo_path)
    le_oponente = joblib.load(le_oponente_path)

    xg_path = os.path.join(DATA_DIR, 'xg_data.json')
    try:
        with open(xg_path, 'r') as f:
            xg_db = json.load(f)
        xg_favor = xg_db.get(equipo, {}).get('xg_favor', 1.2)
        xg_contra = xg_db.get(equipo, {}).get('xg_contra', 0.9)
    except FileNotFoundError:
        print(f"ADVERTENCIA: {xg_path} no encontrado, usando xG por defecto")
        xg_favor = 1.2
        xg_contra = 0.9
    except json.JSONDecodeError as e:
        raise ConfigurationError(f"xg_data.json tiene formato inválido: {e}") from e

    if equipo not in le_equipo.classes_:
        raise PredictionError(
            f"Equipo '{equipo}' no encontrado en el encoder. "
            f"Equipos disponibles: {list(le_equipo.classes_)}"
        )
    if oponente not in le_oponente.classes_:
        raise PredictionError(
            f"Oponente '{oponente}' no encontrado en el encoder. "
            f"Oponentes disponibles: {list(le_oponente.classes_)}"
        )

    e_cod = le_equipo.transform([equipo])[0]
    o_cod = le_oponente.transform([oponente])[0]

    xg_diferencia = xg_favor - xg_contra
    xg_ratio = xg_favor / (xg_contra + 0.01)
    xg_total = xg_favor + xg_contra

    input_data = pd.DataFrame([[xg_favor, xg_contra, xg_diferencia, xg_ratio, xg_total,
                                importancia_partido, dias_descanso, e_cod, o_cod]],
                              columns=['xg_favor', 'xg_contra', 'xg_diferencia', 'xg_ratio', 'xg_total',
                                      'importancia_partido', 'dias_descanso', 'equipo_encoded', 'oponente_encoded'])

    prob = modelo.predict_proba(input_data)[0]
    print(f"Predicción para {equipo} vs {oponente}:")
    print(f"xG {equipo}: {xg_favor} favor / {xg_contra} contra")
    print(f"Importancia partido: {importancia_partido}, Días descanso: {dias_descanso}")
    print(f"Probabilidad de victoria: {prob[1]*100:.2f}%")
    return prob

if __name__ == "__main__":
    if len(sys.argv) == 3:
        predecir(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 5:
        predecir(sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]))
    else:
        print("Uso: python predecir.py equipo oponente [importancia_partido] [dias_descanso]")
        print("Ejemplo: python predecir.py Argentina Austria 1.5 7")
