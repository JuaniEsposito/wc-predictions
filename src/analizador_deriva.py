import pandas as pd
import os
from datetime import datetime, timedelta
from src.exceptions import DataValidationError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def analizar_deriva(dataset_path=None):
    """
    Analiza la deriva de datos comparando xG promedio del último mes
    contra el promedio histórico del dataset.
    
    Si la diferencia es > 15%, lanza alerta de modelo desactualizado.
    """
    if dataset_path is None:
        dataset_path = os.path.join(DATA_DIR, 'dataset_mundial.csv')
    
    if not os.path.exists(dataset_path):
        print(f"⚠️  No se encontró {dataset_path}. Saltando análisis de deriva.")
        return True
    df = pd.read_csv(dataset_path)
    
    required_cols = ['xg_favor', 'fecha']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise DataValidationError(f"Dataset no tiene columnas necesarias: {missing}")
    
    print("🔍 Analizando deriva de datos...")
    
    # Convertir fecha a datetime
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df = df.dropna(subset=['fecha'])
    
    if len(df) == 0:
        print("⚠️  Dataset vacío después de filtrar fechas. Saltando análisis.")
        return True
    
    # Calcular promedio histórico de xG
    promedio_historico = df['xg_favor'].mean()
    
    # Determinar fecha más reciente
    fecha_max = df['fecha'].max()
    fecha_un_mes_antes = fecha_max - timedelta(days=30)
    
    # Filtrar datos del último mes
    df_ultimo_mes = df[df['fecha'] >= fecha_un_mes_antes]
    
    if len(df_ultimo_mes) == 0:
        print("⚠️  No hay datos del último mes. Usando todo el dataset como referencia.")
        promedio_reciente = promedio_historico
    else:
        promedio_reciente = df_ultimo_mes['xg_favor'].mean()
    
    # Calcular diferencia porcentual
    if promedio_historico > 0:
        diferencia_porcentual = abs((promedio_reciente - promedio_historico) / promedio_historico) * 100
    else:
        diferencia_porcentual = 0
    
    print(f"   📊 Promedio histórico xG: {promedio_historico:.3f}")
    print(f"   📊 Promedio reciente xG: {promedio_reciente:.3f}")
    print(f"   📊 Diferencia: {diferencia_porcentual:.1f}%")
    
    # Verificar umbral de alerta (25% para datasets mixtos)
    if diferencia_porcentual > 25:
        print("🚨 ALERTA DE DERIVA: Modelo desactualizado")
        print("   ⚠️  La distribución de xG ha cambiado significativamente (>25%)")
        print("   💡 Recomendación: Reentrenar el modelo con datos más recientes")
        return False
    else:
        print("✅ Deriva dentro de límites aceptables (<25%)")
        return True

if __name__ == "__main__":
    if analizar_deriva():
        exit(0)
    else:
        exit(1)
