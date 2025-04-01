import requests
from datetime import datetime
import json

API_KEY = "AymenURP9kWkgEatcBdcYA"
SEASON_ID = "47663"
url = f"https://volleyball.sportdevs.com/matches?season_id=eq.{SEASON_ID}"

headers = {
    'Accept': 'application/json',
    "Authorization": f"Bearer {API_KEY}"
}

def format_score(score_data):
    if not score_data:
        return "N/D"
    
    periods = []
    for i in range(1, 6):  # Considera fino a 5 set
        period_key = f"period_{i}"
        if period_key in score_data:
            periods.append(f"Set {i}: {score_data[period_key]}")
    
    current_score = f"{score_data.get('current', '?')}-{score_data.get('display', '?')}"
    return f"{current_score} ({'; '.join(periods)})"

def format_time(time_str):
    try:
        dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S+00:00")
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return time_str

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    matches = response.json()

    if not matches:
        print("Nessuna partita trovata per questa stagione.")
    else:
        print("\n" + "="*80)
        print(f" SUPERLEGA VOLLEY 24/25 - RISULTATI PARTITE ".center(80, " "))
        print("="*80 + "\n")

        for match in matches:
            # Informazioni base
            print(f"\n📌 {match['name']}")
            print(f"🆔 ID Partita: {match['id']}")
            print(f"📅 Data: {format_time(match.get('start_time', 'N/D'))}")
            print(f"🏟️ Arena: {match.get('arena_name', 'N/D')}")
            
            # Squadre e punteggio
            print("\n🏐 SQUADRE:")
            print(f"  🏠 {match['home_team_name']} - {format_score(match.get('home_team_score', {}))}")
            print(f"  ✈️ {match['away_team_name']} - {format_score(match.get('away_team_score', {}))}")
            
            # Dettagli partita
            print("\nℹ️ DETTAGLI:")
            print(f"  🏆 Competizione: {match.get('tournament_name', 'N/D')}")
            print(f"  🔄 Round: {match.get('round', {}).get('round', 'N/D')}")
            print(f"  ⏱ Durata: {match.get('duration', 'N/D')} secondi")
            
            # Allenatori
            if 'coaches' in match:
                print("\n👨‍🏫 ALLENATORI:")
                if 'home_coach_name' in match['coaches']:
                    print(f"  🏠 {match['coaches']['home_coach_name']}")
                if 'away_coach_name' in match['coaches']:
                    print(f"  ✈️ {match['coaches']['away_coach_name']}")
            
            print("\n" + "-"*80)

except requests.exceptions.RequestException as e:
    print(f"❌ Errore nella richiesta API: {str(e)}")
except json.JSONDecodeError:
    print("❌ Errore nella decodifica della risposta JSON")
except Exception as e:
    print(f"❌ Errore imprevisto: {str(e)}")