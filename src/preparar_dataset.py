import os
import pandas as pd
import frontmatter
from sklearn.preprocessing import LabelEncoder
import joblib
import json
from src.exceptions import DataValidationError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI_DIR = os.path.join(BASE_DIR, 'wiki')
DATA_DIR = os.path.join(BASE_DIR, 'data')

def parse_result(res_str):
    try:
        parts = res_str.split('-')
        if len(parts) != 2:
            raise ValueError(f"Formato de resultado inesperado: '{res_str}'")
        return int(parts[0]), int(parts[1])
    except (ValueError, AttributeError) as e:
        raise DataValidationError(f"No se pudo parsear resultado '{res_str}': {e}") from e

def inyectar_xg(df):
    """
    Inyecta valores de xG desde el archivo JSON basados en el equipo.
    """
    xg_path = os.path.join(DATA_DIR, 'xg_data.json')
    try:
        with open(xg_path, 'r') as f:
            xg_db = json.load(f)
    except FileNotFoundError:
        print(f"ADVERTENCIA: {xg_path} no encontrado, usando xG por defecto (1.0)")
        df['xg_favor'] = 1.0
        df['xg_contra'] = 1.0
        return df
    except json.JSONDecodeError as e:
        raise DataValidationError(f"xg_data.json tiene formato inválido: {e}") from e

    df['xg_favor'] = df['equipo'].map(lambda x: xg_db.get(x, {}).get('xg_favor', 1.0))
    df['xg_contra'] = df['equipo'].map(lambda x: xg_db.get(x, {}).get('xg_contra', 1.0))
    print("xG inyectado desde xg_data.json")
    return df

def preparar_dataset():
    dataset_path = os.path.join(DATA_DIR, 'dataset_real.csv')
    if os.path.exists(dataset_path):
        print("Usando dataset real de la API...")
        df = pd.read_csv(dataset_path)

        columnas_requeridas = ['equipo', 'oponente', 'goles_favor', 'goles_contra', 'victoria']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        if columnas_faltantes:
            raise DataValidationError(
                f"El CSV no tiene las columnas requeridas. "
                f"Faltan: {columnas_faltantes}. Encontradas: {list(df.columns)}"
            )

        df = inyectar_xg(df)

    else:
        data = []
        parse_errors = []

        if not os.path.exists(WIKI_DIR):
            raise DataValidationError(
                f"No hay datos: ni dataset_real.csv ni directorio wiki ({WIKI_DIR}). "
                "Ejecuta primero central_de_datos.py para obtener datos de la API."
            )

        for root, dirs, files in os.walk(WIKI_DIR):
            for file in files:
                if file.endswith('.md') and file != 'INDEX.md':
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            post = frontmatter.load(f)
                            m = post.metadata

                            resultado_str = m.get('resultado', '0-0')
                            try:
                                g_f, g_c = parse_result(resultado_str)
                            except DataValidationError:
                                parse_errors.append((file_path, resultado_str))
                                g_f, g_c = 0, 0

                            data.append({
                                'equipo': m.get('equipo'),
                                'oponente': m.get('oponente'),
                                'goles_favor': g_f,
                                'goles_contra': g_c,
                                'xg_favor': float(m.get('xg_favor', 0.0)),
                                'xg_contra': float(m.get('xg_contra', 0.0)),
                                'victoria': 1 if g_f > g_c else 0
                            })
                    except Exception as e:
                        print(f"Error leyendo {file_path}: {e}")
                        parse_errors.append((file_path, str(e)))

        if parse_errors:
            print(f"ADVERTENCIA: {len(parse_errors)} archivos con errores de parseo")

        df = pd.DataFrame(data)

        if df.empty:
            raise DataValidationError(
                "No hay datos en el directorio wiki ni dataset real. "
                "Ejecuta primero central_de_datos.py para obtener datos de la API."
            )

    le_equipo = LabelEncoder()
    le_oponente = LabelEncoder()

    todos_equipos = pd.concat([df['equipo'], df['oponente']]).unique()
    le_equipo.fit(todos_equipos)
    le_oponente.fit(df['oponente'].unique())

    df['equipo_encoded'] = le_equipo.transform(df['equipo'])
    df['oponente_encoded'] = le_oponente.transform(df['oponente'])

    joblib.dump(le_equipo, os.path.join(DATA_DIR, 'le_equipo.pkl'))
    joblib.dump(le_oponente, os.path.join(DATA_DIR, 'le_oponente.pkl'))

    df.to_csv(os.path.join(DATA_DIR, 'dataset_mundial.csv'), index=False)
    print("Dataset generado con éxito: dataset_mundial.csv")
    print(df.head())
    print(f"\nEncoders guardados: le_equipo.pkl, le_oponente.pkl")
    print(f"Total de equipos únicos codificados: {len(todos_equipos)}")

if __name__ == "__main__":
    preparar_dataset()
