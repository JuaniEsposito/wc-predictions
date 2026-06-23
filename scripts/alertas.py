#!/usr/bin/env python3
"""
Monitor de Fatiga Crítica
Alerta cuando un equipo juega con pocos días de descanso
Información valiosa para apostadores y analistas
"""

import pandas as pd
from datetime import datetime, timedelta
import sys

def analizar_fatiga_critica(equipo=None, dias_minimo=3):
    """
    Analiza la fatiga de equipos basándose en días de descanso
    """
    # Cargar dataset
    df = pd.read_csv('dataset_mundial.csv')
    
    print("🚨 MONITOR DE FATIGA CRÍTICA")
    print("=" * 60)
    print(f"Umbral de alerta: {dias_minimo} días de descanso")
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d')}")
    print()
    
    if equipo:
        # Análisis específico de un equipo
        equipo_data = df[df['equipo'] == equipo].copy()
        if len(equipo_data) == 0:
            print(f"❌ Equipo '{equipo}' no encontrado en el dataset")
            return
        
        # Ordenar por fecha
        equipo_data['fecha'] = pd.to_datetime(equipo_data['fecha'], errors='coerce')
        equipo_data = equipo_data.sort_values('fecha', ascending=False)
        
        if len(equipo_data) > 0:
            ultimo_partido = equipo_data.iloc[0]
            dias_descanso = ultimo_partido.get('dias_descanso', 7)
            
            print(f"📊 ANÁLISIS DE FATIGA: {equipo}")
            print(f"Último partido: {ultimo_partido['fecha'].strftime('%Y-%m-%d')}")
            print(f"Días de descanso: {dias_descanso}")
            print(f"Oponente: {ultimo_partido['oponente']}")
            print()
            
            if dias_descanso < dias_minimo:
                print(f"🚨 ¡ALERTA CRÍTICA! {equipo} juega con solo {dias_descanso} días de descanso")
                print(f"   ⚠️  Riesgo de fatiga: ALTO")
                print(f"   💡 Recomendación: Considerar rotación o rendimiento reducido")
            elif dias_descanso < 5:
                print(f"⚠️  ALERTA MODERADO: {equipo} tiene {dias_descanso} días de descanso")
                print(f"   ⚠️  Riesgo de fatiga: MEDIO")
            else:
                print(f"✅ {equipo} tiene descanso suficiente ({dias_descanso} días)")
                print(f"   ✅ Riesgo de fatiga: BAJO")
    else:
        # Análisis de todos los equipos
        equipos_criticos = df[df['dias_descanso'] < dias_minimo].copy()
        
        if len(equipos_criticos) == 0:
            print("✅ No hay equipos con fatiga crítica en el dataset")
            return
        
        print(f"🚨 EQUIPOS CON FATIGA CRÍTICA ({len(equipos_criticos)}):")
        print()
        
        for _, row in equipos_criticos.iterrows():
            dias = row['dias_descanso']
            equipo = row['equipo']
            oponente = row['oponente']
            fecha = row['fecha']
            
            nivel_riesgo = "🔴 ALTO" if dias < 2 else "🟡 MEDIO"
            
            print(f"{nivel_riesgo} | {equipo:20s} | {dias} días descanso | vs {oponente}")
        
        print()
        print("💡 ANÁLISIS DE IMPACTO:")
        print("   - Fatiga alta puede reducir rendimiento hasta 15-20%")
        print("   - Considerar esto en predicciones y apuestas")
        print("   - Equipos con <2 días: riesgo de lesiones aumentado")

def generar_reporte_completo():
    """
    Genera un reporte completo de fatiga para todos los equipos
    """
    df = pd.read_csv('dataset_mundial.csv')
    
    print("\n📋 REPORTE COMPLETO DE FATIGA")
    print("=" * 60)
    
    # Estadísticas generales
    promedio_descanso = df['dias_descanso'].mean()
    min_descanso = df['dias_descanso'].min()
    max_descanso = df['dias_descanso'].max()
    
    print(f"Promedio días descanso: {promedio_descanso:.1f}")
    print(f"Mínimo días descanso: {min_descanso}")
    print(f"Máximo días descanso: {max_descanso}")
    print()
    
    # Distribución de fatiga
    fatiga_alta = len(df[df['dias_descanso'] < 3])
    fatiga_media = len(df[(df['dias_descanso'] >= 3) & (df['dias_descanso'] < 5)])
    fatiga_baja = len(df[df['dias_descanso'] >= 5])
    
    print(f"🔴 Fatiga alta (<3 días): {fatiga_alta} equipos")
    print(f"🟡 Fatiga media (3-4 días): {fatiga_media} equipos")
    print(f"🟢 Fatiga baja (>=5 días): {fatiga_baja} equipos")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Análisis de equipo específico
        equipo = sys.argv[1]
        dias_minimo = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        analizar_fatiga_critica(equipo, dias_minimo)
    else:
        # Análisis de todos los equipos
        analizar_fatiga_critica()
        generar_reporte_completo()
