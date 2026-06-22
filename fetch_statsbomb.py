import pandas as pd
import os
from statsbombpy import sb
import warnings

warnings.filterwarnings('ignore')

def fetch_statsbomb_events(match_ids=None):
    """
    Extrae eventos tácticos (pases, tiros, presión) de partidos específicos por ID.
    ADVERTENCIA: Esta operación es pesada y lenta.
    NO usar para el pipeline de predicción básico.
    """
    print("⚠️  ADVERTENCIA: Esta operación es pesada y lenta.")
    print("   Solo usar para análisis táctico profundo de partidos específicos.")
    
    if not match_ids:
        print("❌ Error: Debes especificar IDs de partidos (ej: python fetch_statsbomb.py 3788741)")
        return
    
    try:
        events_data = []
        
        for match_id in match_ids:
            print(f"📊 Procesando partido ID: {match_id}...")
            
            try:
                # Obtener eventos del partido
                events = sb.events(match_id=match_id)
                
                # Filtrar eventos tácticos relevantes
                tactical_events = events[events['type'].isin(['Pass', 'Shot', 'Pressure'])]
                
                for idx, event in tactical_events.iterrows():
                    events_data.append({
                        "match_id": match_id,
                        "evento_tipo": event.get('type', 'Unknown'),
                        "equipo": event.get('team', 'Unknown'),
                        "jugador": event.get('player', 'Unknown'),
                        "minuto": event.get('minute', 0),
                        "detalles": str(event.get('pass', {})) if event.get('type') == 'Pass' else str(event.get('shot', {})) if event.get('type') == 'Shot' else '',
                        "fuente": "statsbomb",
                    })
                
                print(f"   ✅ {len(tactical_events)} eventos tácticos extraídos")
                
            except Exception as e:
                print(f"   ❌ Error procesando partido {match_id}: {e}")
                continue
        
        if events_data:
            # Guardar CSV
            os.makedirs("data", exist_ok=True)
            df_output = pd.DataFrame(events_data)
            df_output.to_csv("data/statsbomb_events.csv", index=False)
            print(f"✅ Total: {len(events_data)} eventos -> data/statsbomb_events.csv")
        else:
            print("⚠️  No se extrajeron eventos")
            
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python fetch_statsbomb.py <match_id1> <match_id2> ...")
        print("Ejemplo: python fetch_statsbomb.py 3788741 3788742")
        sys.exit(1)
    
    # Convertir argumentos a enteros (IDs de partidos)
    match_ids = [int(arg) for arg in sys.argv[1:]]
    
    fetch_statsbomb_events(match_ids)
