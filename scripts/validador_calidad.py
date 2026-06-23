import pandas as pd
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
WIKI_DIR = os.path.join(BASE_DIR, 'wiki')

def validar_datos():
    """
    Validador de Contrato de Datos - Actúa como "portero" del pipeline
    Verifica que los datos cumplan con los límites lógicos definidos
    """
    contract_path = os.path.join(WIKI_DIR, 'data_contract.json')
    dataset_path = os.path.join(DATA_DIR, 'dataset_mundial.csv')
    
    # Cargar contrato de datos
    try:
        with open(contract_path, 'r') as f:
            contract = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el contrato de datos en {contract_path}")
        return False
    
    # Cargar dataset
    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError:
        print(f"⚠️  Advertencia: No se encontró dataset en {dataset_path}")
        print("   Esto es normal si es la primera ejecución. Continuando...")
        return True
    
    print(f"📋 Validando contrato de datos ({len(df)} registros)...")
    
    # 1. Chequeo de columnas obligatorias
    columnas_faltantes = []
    for col in contract['columnas_obligatorias']:
        if col not in df.columns:
            columnas_faltantes.append(col)
    
    if columnas_faltantes:
        print(f"❌ Error: Faltan columnas obligatorias: {columnas_faltantes}")
        return False
    
    # 2. Chequeo de rangos (xG)
    if 'xg_favor' in df.columns:
        xg_invalidos = df[df['xg_favor'] > contract['xG_max']]
        if len(xg_invalidos) > 0:
            print(f"⚠️  Alerta: {len(xg_invalidos)} registros con xG fuera de rango (> {contract['xG_max']})")
            print(f"   Máximo encontrado: {df['xg_favor'].max()}")
            return False
        
        xg_negativos = df[df['xg_favor'] < contract['xG_min']]
        if len(xg_negativos) > 0:
            print(f"⚠️  Alerta: {len(xg_negativos)} registros con xG negativo")
            return False
    
    # 3. Chequeo de días de descanso
    if 'dias_descanso' in df.columns:
        descanso_invalidos = df[df['dias_descanso'] > contract['dias_descanso_max']]
        if len(descanso_invalidos) > 0:
            print(f"⚠️  Alerta: {len(descanso_invalidos)} registros con días de descanso fuera de rango (> {contract['dias_descanso_max']})")
            print(f"   Máximo encontrado: {df['dias_descanso'].max()}")
            return False
    
    # 4. Chequeo de importancia de partido
    if 'importancia_partido' in df.columns:
        importancia_invalida = df[df['importancia_partido'] > contract['importancia_partido_max']]
        if len(importancia_invalida) > 0:
            print(f"⚠️  Alerta: {len(importancia_invalida)} registros con importancia fuera de rango (> {contract['importancia_partido_max']})")
            print(f"   Máximo encontrado: {df['importancia_partido'].max()}")
            return False
    
    # 5. Chequeo de valores nulos en columnas críticas
    columnas_criticas = ['equipo', 'oponente', 'goles_favor']
    for col in columnas_criticas:
        if col in df.columns and df[col].isnull().any():
            nulos = df[col].isnull().sum()
            print(f"❌ Error: {nulos} valores nulos en columna crítica '{col}'")
            return False
    
    print("✅ Contrato de datos validado correctamente.")
    print(f"   - {len(df)} registros válidos")
    print(f"   - Todas las columnas obligatorias presentes")
    print(f"   - Rangos dentro de límites aceptables")
    return True

if __name__ == "__main__":
    if validar_datos():
        exit(0)
    else:
        exit(1)
