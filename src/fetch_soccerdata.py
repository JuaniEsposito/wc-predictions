import pandas as pd
import os
from datetime import datetime
import soccerdata as sd
from src.exceptions import DataFetchError

def fetch_historical_matches(league="ENG-Premier League", seasons=2):
    """
    Trae histórico de los últimos N años de una liga específica usando soccerdata.
    Normaliza al formato CSV estándar con columna fuente="soccerdata".
    """
    print(f"Obteniendo datos históricos de {league} (últimos {seasons} años)...")

    current_year = datetime.now().year
    season_list = [str(current_year - i) for i in range(seasons)]

    try:
        league_reader = sd.MatchHistory(league, seasons=season_list)
        df = league_reader.read_games()
    except Exception as e:
        raise DataFetchError(f"Error al obtener datos históricos de {league}: {e}") from e

    if df.empty:
        raise DataFetchError(f"No se encontraron datos para {league} temporadas {season_list}")

    matches = []
    for _, row in df.iterrows():
        home_team = row.get('home_team', 'Unknown')
        away_team = row.get('away_team', 'Unknown')
        date = row.get('date', '')
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

    os.makedirs("data", exist_ok=True)
    df_output = pd.DataFrame(matches)
    df_output.to_csv("data/historical_matches.csv", index=False)
    print(f"OK: {len(matches)} partidos -> data/historical_matches.csv")
    return matches

if __name__ == "__main__":
    import sys
    league = sys.argv[1] if len(sys.argv) > 1 else "ENG-Premier League"
    seasons = int(sys.argv[2]) if len(sys.argv) > 2 else 2

    fetch_historical_matches(league, seasons)
