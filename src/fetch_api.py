import requests
import pandas as pd
import os
from dotenv import load_dotenv
from src.exceptions import ConfigurationError, DataFetchError

load_dotenv()
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
HEADERS = {"X-Auth-Token": API_KEY}
URL = "https://api.football-data.org/v4/matches"

def fetch_live_matches():
    if not API_KEY:
        raise ConfigurationError("Falta FOOTBALL_DATA_API_KEY en .env")

    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
    except requests.ConnectionError as e:
        raise DataFetchError(f"No se pudo conectar a {URL}") from e
    except requests.Timeout as e:
        raise DataFetchError(f"Timeout al conectar a {URL}") from e

    if response.status_code == 429:
        raise DataFetchError("Error 429: límite de requests excedido, esperar antes de reintentar")
    if response.status_code != 200:
        raise DataFetchError(f"Error {response.status_code}: {response.text[:200]}")

    data = response.json()
    matches = []
    for match in data.get("matches", []):
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]
        score = match.get("score", {}).get("fullTime", {})
        matches.append({
            "equipo": home,
            "oponente": away,
            "partido": f"{home}_vs_{away}",
            "fecha": match["utcDate"],
            "resultado": f"{score.get('home', '-')}-{score.get('away', '-')}",
            "fuente": "api",
        })
    os.makedirs("data", exist_ok=True)
    pd.DataFrame(matches).to_csv("data/live_matches.csv", index=False)
    print(f"OK: {len(matches)} partidos -> data/live_matches.csv")
    return matches

if __name__ == "__main__":
    fetch_live_matches()
