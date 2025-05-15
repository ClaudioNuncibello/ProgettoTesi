import requests
import time
import os
from datetime import datetime
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_KEY = "AymenURP9kWkgEatcBdcYA"
MATCHES_URL = "https://volleyball.sportdevs.com/matches?status_type=eq.live"

HEADERS = {
    'Accept': 'application/json',
    "Authorization": f"Bearer {API_KEY}"
}

# crea una session con retry automatici
def create_session():
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.headers.update(HEADERS)
    return session

session = create_session()

def get_team_total_points(score_map):
    return sum(v for k, v in score_map.items()
               if k.startswith("period_") and isinstance(v, int))

def get_current_set_info(reason):
    try:
        return int(reason.split()[0].strip('stndrdth'))
    except:
        return 1

def format_set_scores(home_scores, away_scores, current_set):
    parts = []
    for i in range(1, current_set + 1):
        h = home_scores.get(f"period_{i}", "?")
        a = away_scores.get(f"period_{i}", "?")
        parts.append(f"Set {i}: {h}-{a}")
    return " | ".join(parts)

while True:
    try:
        # timeout più generoso
        resp = session.get(MATCHES_URL, timeout=10)
        resp.raise_for_status()
        matches = resp.json()

        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\nUltimo aggiornamento: {datetime.now().strftime('%H:%M:%S')}\n")

        rows = []
        for m in matches:
            hs = m["home_team_score"]
            as_ = m["away_team_score"]
            # se sono liste, prendi il primo elemento
            if isinstance(hs, list): hs = hs[0]
            if isinstance(as_, list): as_ = as_[0]

            home_sets = hs.get("display", 0)
            away_sets = as_.get("display", 0)
            home_total = get_team_total_points(hs)
            away_total = get_team_total_points(as_)
            status = m.get("status", {}).get("reason", "")

            current_set = get_current_set_info(status)

            home_score_map = m["home_team_score"]
            away_score_map = m["away_team_score"]
            home_current_score = home_score_map.get(f"period_{current_set}", '?')
            away_current_score = away_score_map.get(f"period_{current_set}", '?')

            set_info = format_set_scores(hs, as_, current_set)
            duration = m.get("duration", 0)
            game_duration = f"{duration//60}m {duration%60}s"

            # stampa a video
            print(f"📊 {m['home_team_name']} vs {m['away_team_name']} | Totale punti: {home_total}-{away_total} | Set: {home_sets}-{away_sets}")
            print(f"  🏠 Attuale: {home_current_score} | ✈️ Attuale: {away_current_score}")
            print(f"  🎯 {set_info}")
            print(f"  🔄 Stato: {status} | ⏱ {game_duration}\n")

            rows.append({
                "match_id": m["id"],
                "timestamp": datetime.now(),
                "home_team_id": m["home_team_id"],
                "away_team_id": m["away_team_id"],
                "home_sets_won": home_sets,
                "away_sets_won": away_sets,
                "home_score_total": home_total,
                "away_score_total": away_total,
                "set_diff": home_sets - away_sets,
                "score_diff": home_total - away_total,
                "current_set": current_set,
                "set_info": set_info,
                "game_duration": game_duration,
                "match_status": status
            })

        # mostra anche il DataFrame
        df = pd.DataFrame(rows)
        print("\n🧾 DataFrame attuale:")
        print(df)

        # aspetto 10s prima del prossimo pull
        time.sleep(10)

    except requests.exceptions.ReadTimeout:
        print("⚠️ Timeout nella richiesta (10s). Riprovo tra 5s…")
        time.sleep(5)
        continue

    except requests.exceptions.RequestException as e:
        print(f"❌ Errore nella richiesta API: {e}\n— aspetto 10s e riprovo…")
        time.sleep(10)
        continue

    except Exception as e:
        print(f"❌ Errore nel parsing dei dati: {e}\n— aspetto 10s e riprovo…")
        time.sleep(10)
        continue
