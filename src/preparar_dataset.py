import os
import pandas as pd
import frontmatter
from sklearn.preprocessing import LabelEncoder
import joblib
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI_DIR = os.path.join(BASE_DIR, 'wiki')
DATA_DIR = os.path.join(BASE_DIR, 'data')

def parse_result(res_str):
    # Convierte "2-0" en goles_favor=2, goles_contra=0
    try:
        f, c = res_str.split('-')
        return int(f), int(c)
    except (ValueError, IndexError):
        return 0, 0

def inyectar_xg(df):
    """
    Inyecta valores de xG desde el archivo JSON basados en el equipo.
    """
    try:
        xg_path = os.path.join(DATA_DIR, 'xg_data.json')
        with open(xg_path, 'r') as f:
            xg_db = json.load(f)
        
        # Mapear los valores de xG basados en el equipo
        df['xg_favor'] = df['equipo'].map(lambda x: xg_db.get(x, {}).get('xg_favor', 1.0))
        df['xg_contra'] = df['equipo'].map(lambda x: xg_db.get(x, {}).get('xg_contra', 1.0))
        print("✅ xG inyectado desde xg_data.json")
        return df
    except Exception as e:
        print(f"⚠️  Error inyectando xG: {e}")
        print("   Usando valores por defecto (1.0)")
        df['xg_favor'] = 1.0
        df['xg_contra'] = 1.0
        return df

def preparar_dataset():
    # Verificar si existe dataset_real.csv (del API-only approach)
    dataset_path = os.path.join(DATA_DIR, 'dataset_real.csv')
    if os.path.exists(dataset_path):
        print("📊 Usando dataset real de la API...")
        df = pd.read_csv(dataset_path)
        
        # Validar columnas
        columnas_requeridas = ['equipo', 'oponente', 'goles_favor', 'goles_contra', 'victoria']
        if not all(col in df.columns for col in columnas_requeridas):
            print(f"❌ Error: El CSV no tiene el formato correcto. Columnas requeridas: {columnas_requeridas}")
            print(f"   Columnas encontradas: {list(df.columns)}")
            return
        
        # Inyectar xG desde el archivo JSON
        df = inyectar_xg(df)
        
        # Continuar con el procesamiento normal
    else:
        # Procesar archivos wiki (método original)
        data = []
        
        for root, dirs, files in os.walk(WIKI_DIR):
            for file in files:
                if file.endswith('.md') and file != 'INDEX.md':
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        post = frontmatter.load(f)
                        m = post.metadata
                        
                        g_f, g_c = parse_result(m.get('resultado', '0-0'))
                        
                        data.append({
                            'equipo': m.get('equipo'),
                            'oponente': m.get('oponente'),
                            'goles_favor': g_f,
                            'goles_contra': g_c,
                            # Nueva lógica para xG: si no existe en el frontmatter, usa 0.0
                            'xg_favor': float(m.get('xg_favor', 0.0)),
                            'xg_contra': float(m.get('xg_contra', 0.0)),
                            'victoria': 1 if g_f > g_c else 0
                        })
        
        df = pd.DataFrame(data)
        
        # Verificar si hay datos antes de procesar
        if df.empty:
            print("⚠️  No hay datos en el directorio wiki ni dataset real.")
            print("   Ejecuta primero central_de_datos.py para obtener datos de la API.")
            return
    
    # Codificar nombres de equipos y oponentes a números
    le_equipo = LabelEncoder()
    le_oponente = LabelEncoder()
    
    # Fit con todos los equipos únicos (tanto equipo como oponente)
    todos_equipos = pd.concat([df['equipo'], df['oponente']]).unique()
    le_equipo.fit(todos_equipos)
    le_oponente.fit(df['oponente'].unique())
    
    # Transformar datos
    df['equipo_encoded'] = le_equipo.transform(df['equipo'])
    df['oponente_encoded'] = le_oponente.transform(df['oponente'])
    
    # Guardar encoders para uso futuro
    joblib.dump(le_equipo, os.path.join(DATA_DIR, 'le_equipo.pkl'))
    joblib.dump(le_oponente, os.path.join(DATA_DIR, 'le_oponente.pkl'))
    
    # Guardar dataset con columnas codificadas
    df.to_csv(os.path.join(DATA_DIR, 'dataset_mundial.csv'), index=False)
    print("Dataset generado con éxito: dataset_mundial.csv")
    print(df.head())
    print(f"\nEncoders guardados: le_equipo.pkl, le_oponente.pkl")
    print(f"Total de equipos únicos codificados: {len(todos_equipos)}")

if __name__ == "__main__":
    preparar_dataset()
