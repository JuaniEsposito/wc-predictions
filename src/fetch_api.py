import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
HEADERS = {"X-Auth-Token": API_KEY}
URL = "https://api.football-data.org/v4/matches"

def fetch_live_matches():
    if not API_KEY:
        print("Error: falta FOOTBALL_DATA_API_KEY en .env")
        return
    response = requests.get(URL, headers=HEADERS, timeout=10)
    if response.status_code == 200:
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
    elif response.status_code == 429:
        print("Error 429: límite de requests excedido, esperar antes de reintentar")
    else:
        print(f"Error {response.status_code}")

if __name__ == "__main__":
    fetch_live_matches()
