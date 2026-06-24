import pandas as pd
import joblib
import os
from src.utils import DATA_DIR


def verificar():
    dataset_path = os.path.join(DATA_DIR, 'dataset_real.csv')
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"No se encontró {dataset_path}. Ejecuta primero el pipeline.")
    df = pd.read_csv(dataset_path)

    encoder_equipo_path = os.path.join(DATA_DIR, 'le_equipo.pkl')
    encoder_oponente_path = os.path.join(DATA_DIR, 'le_oponente.pkl')
    if not os.path.exists(encoder_equipo_path):
        raise FileNotFoundError(f"No se encontró {encoder_equipo_path}. Ejecuta primero entrenar_modelo.py")
    if not os.path.exists(encoder_oponente_path):
        raise FileNotFoundError(f"No se encontró {encoder_oponente_path}. Ejecuta primero entrenar_modelo.py")

    le_equipo = joblib.load(encoder_equipo_path)
    le_oponente = joblib.load(encoder_oponente_path)

    print("Equipos en el encoder:")
    print(le_equipo.classes_)
    print(f"\nTotal equipos en encoder: {len(le_equipo.classes_)}")

    print("\nVerificación de equipos específicos:")
    for team in ['Egypt', 'New Zealand']:
        if team in le_equipo.classes_:
            print(f"{team}: ESTÁ en el encoder")
        else:
            print(f"{team}: NO está en el encoder")

    check = df[df['equipo'].isin(['Argentina', 'Egypt', 'Austria', 'New Zealand'])]
    print("\nPartidos encontrados en dataset:")
    print(check[['equipo', 'oponente', 'goles_favor', 'goles_contra', 'fecha']])
    print(f"\nTotal partidos encontrados: {len(check)}")


if __name__ == "__main__":
    verificar()
