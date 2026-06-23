import sys
import pandas as pd
import joblib
import json

def predecir(equipo, oponente, importancia_partido=1.0, dias_descanso=7):
    modelo = joblib.load('modelo_ganador.pkl')
    le_equipo = joblib.load('le_equipo.pkl')
    le_oponente = joblib.load('le_oponente.pkl')
    
    # Cargar datos xG
    try:
        with open('data/xg_data.json', 'r') as f:
            xg_db = json.load(f)
        xg_favor = xg_db.get(equipo, {}).get('xg_favor', 1.2)
        xg_contra = xg_db.get(equipo, {}).get('xg_contra', 0.9)
    except:
        xg_favor = 1.2
        xg_contra = 0.9
    
    # Transformamos nombres a códigos
    try:
        e_cod = le_equipo.transform([equipo])[0]
        o_cod = le_oponente.transform([oponente])[0]
        
        # Usamos los valores xG reales del equipo
        xg_diferencia = xg_favor - xg_contra
        xg_ratio = xg_favor / (xg_contra + 0.01)
        xg_total = xg_favor + xg_contra
        
        # Features elite
        input_data = pd.DataFrame([[xg_favor, xg_contra, xg_diferencia, xg_ratio, xg_total, 
                                    importancia_partido, dias_descanso, e_cod, o_cod]], 
                                  columns=['xg_favor', 'xg_contra', 'xg_diferencia', 'xg_ratio', 'xg_total', 
                                          'importancia_partido', 'dias_descanso', 'equipo_encoded', 'oponente_encoded'])
        
        prob = modelo.predict_proba(input_data)[0]
        print(f"🔮 Predicción para {equipo} vs {oponente}:")
        print(f"xG {equipo}: {xg_favor} favor / {xg_contra} contra")
        print(f"Importancia partido: {importancia_partido}, Días descanso: {dias_descanso}")
        print(f"DEBUG: EquipoEncoded: {e_cod}, OponenteEncoded: {o_cod}")
        print(f"DEBUG: Probabilidades brutas: {prob}")
        print(f"Probabilidad de victoria: {prob[1]*100:.2f}%")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Asegúrate de escribir bien los nombres de los equipos (ej. 'Argentina').")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        predecir(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 5:
        predecir(sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]))
    else:
        print("Uso: python predecir.py equipo oponente [importancia_partido] [dias_descanso]")
        print("Ejemplo: python predecir.py Argentina Austria 1.5 7")
