import requests
import time
import os
from datetime import datetime

API_KEY = "AymenURP9kWkgEatcBdcYA"
url = "https://volleyball.sportdevs.com/matches?status_type=eq.live"

headers = {
    'Accept': 'application/json',
    "Authorization": f"Bearer {API_KEY}"
}

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_set_scores(home_scores, away_scores, current_set):
    set_info = []
    for i in range(1, current_set + 1):
        home = home_scores.get(f'period_{i}', '?')
        away = away_scores.get(f'period_{i}', '?')
        set_info.append(f"Set {i}: {home}-{away}")
    return " | ".join(set_info)

def get_current_set_info(status_reason):
    try:
        return int(status_reason.split()[0].strip('stndrdth'))
    except:
        return 1

while True:
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        matches = response.json()

        clear()
        
        if not matches:
            print("\n" + "="*60)
            print(" ⚠️  Nessuna partita in diretta al momento ".center(60))
            print("="*60 + "\n")
            print("Aggiornamento automatico ogni 5 secondi...")
        else:
            print("\n" + "="*60)
            print(" 🏐 PARTITE IN DIRETTA LIVE ".center(60))
            print("="*60 + "\n")
            print(f"Ultimo aggiornamento: {datetime.now().strftime('%H:%M:%S')}\n")

            for match in matches:
                # Informazioni base
                print(f"\n🔥 {match['home_team_name']} vs {match['away_team_name']}")
                print(f"🏆 {match.get('league_name', 'Competizione')}")
                print(f"🏟️ {match.get('arena_name', 'Stadio sconosciuto')}")
                
                # Punteggi
                home_score = match.get('home_team_score', {})
                away_score = match.get('away_team_score', {})
                current_set = get_current_set_info(match['status']['reason'])
                
                print("\n📊 PUNTEGGIO:")
                print(f"  🏠 {match['home_team_name']}: {home_score.get('current', '?')}")
                print(f"  ✈️ {match['away_team_name']}: {away_score.get('current', '?')}")
                print(f"\n🎯 Set: {format_set_scores(home_score, away_score, current_set)}")
                print(f"🔄 Stato: {match['status']['reason']}")
                
                # Tempo di gioco
                if 'duration' in match:
                    mins = int(match['duration']) // 60
                    secs = int(match['duration']) % 60
                    print(f"⏱ Tempo: {mins}m {secs}s")
                
                print("\n" + "-"*60)

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Errore di connessione: {str(e)}")
        print("Riprovo tra 10 secondi...")
        time.sleep(10)
        continue
    except Exception as e:
        print(f"\n⚠️ Errore imprevisto: {str(e)}")
        print("Riprovo tra 5 secondi...")
        time.sleep(5)
        continue
    
    time.sleep(10)  # Aggiornamento ogni 10 secondi