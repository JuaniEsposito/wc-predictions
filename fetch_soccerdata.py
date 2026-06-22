import pandas as pd
import os
from datetime import datetime, timedelta
import soccerdata as sd

def fetch_historical_matches(league="ENG-Premier League", seasons=2):
    """
    Trae histórico de los últimos N años de una liga específica usando soccerdata.
    Normaliza al formato CSV estándar con columna fuente="soccerdata".
    """
    try:
        print(f"📊 Obteniendo datos históricos de {league} (últimos {seasons} años)...")
        
        # Calcular temporadas (ej: 2023, 2022 para los últimos 2 años)
        current_year = datetime.now().year
        season_list = [str(current_year - i) for i in range(seasons)]
        
        # Usar soccerdata para obtener datos
        league_reader = sd.MatchHistory(league, seasons=season_list)
        
        # Leer datos
        df = league_reader.read_games()
        
        if df.empty:
            print("⚠️  No se encontraron datos para esta liga/temporada")
            return
        
        # Normalizar al formato estándar
        matches = []
        for idx, row in df.iterrows():
            home_team = row.get('home_team', 'Unknown')
            away_team = row.get('away_team', 'Unknown')
            date = row.get('date', '')
            
            # Obtener resultado
            home_goals = row.get('home_team_score', 0)
            away_goals = row.get('away_team_score', 0)
            resultado = f"{home_goals}-{away_goals}"
            
            matches.append({
                "equipo": home_team,
                "oponente": away_team,
                "partido": f"{home_team}_vs_{away_team}",
                "fecha": str(date),
                "resultado": resultado,
                "fuente": "soccerdata",
            })
        
        # Guardar CSV
        os.makedirs("data", exist_ok=True)
        df_output = pd.DataFrame(matches)
        df_output.to_csv("data/historical_matches.csv", index=False)
        
        print(f"✅ OK: {len(matches)} partidos -> data/historical_matches.csv")
        
    except Exception as e:
        print(f"❌ Error al obtener datos históricos: {e}")
        print("   Posibles causas: liga no encontrada, timeout, o cambios en la estructura de datos")

if __name__ == "__main__":
    # Por defecto, usar Premier League de los últimos 2 años
    # Se puede cambiar la liga pasando argumentos
    import sys
    league = sys.argv[1] if len(sys.argv) > 1 else "ENG-Premier League"
    seasons = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    fetch_historical_matches(league, seasons)
