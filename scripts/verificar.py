import pandas as pd
import joblib

df = pd.read_csv('data/dataset_real.csv')
le_equipo = joblib.load('le_equipo.pkl')
le_oponente = joblib.load('le_oponente.pkl')

print("Equipos en el encoder:")
print(le_equipo.classes_)
print(f"\nTotal equipos en encoder: {len(le_equipo.classes_)}")

# Verificar si Egypt y New Zealand están en el encoder
print("\nVerificación de equipos específicos:")
for team in ['Egypt', 'New Zealand']:
    if team in le_equipo.classes_:
        print(f"✅ {team}: ESTÁ en el encoder")
    else:
        print(f"❌ {team}: NO está en el encoder")

# Filtramos para ver si aparecen esos equipos
check = df[df['equipo'].isin(['Argentina', 'Egypt', 'Austria', 'New Zealand'])]
print("\nPartidos encontrados en dataset:")
print(check[['equipo', 'oponente', 'goles_favor', 'goles_contra', 'fecha']])
print(f"\nTotal partidos encontrados: {len(check)}")
