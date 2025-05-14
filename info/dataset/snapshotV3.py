import requests
import time
import os
from datetime import datetime
import pandas as pd
from collections import defaultdict

API_KEY = "AymenURP9kWkgEatcBdcYA"
MATCHES_URL = "https://volleyball.sportdevs.com/matches?status_type=eq.live"

headers = {
    'Accept': 'application/json',
    "Authorization": f"Bearer {API_KEY}"
}

CACHE_TEAM_MATCHES = {}
CACHE_HEAD2HEAD = {}



def get_team_last15_matches(team_id):
    if team_id in CACHE_TEAM_MATCHES:
        return CACHE_TEAM_MATCHES[team_id]
    url = f"https://volleyball.sportdevs.com/matches?or=(home_team_id.eq.{team_id},away_team_id.eq.{team_id})&order=specific_start_time.desc&limit=15"
    resp = requests.get(url, headers=headers)
    matches = resp.json()
    CACHE_TEAM_MATCHES[team_id] = matches
    return matches


def compute_win_rate(matches, team_id):
    wins, total = 0, 0
    for match in matches:
        home_id = match["home_team_id"]
        away_id = match["away_team_id"]
        home_score = match.get("home_team_score", {}).get("display")
        away_score = match.get("away_team_score", {}).get("display")
        if home_score is None or away_score is None:
            continue
        if team_id == home_id and home_score > away_score:
            wins += 1
        elif team_id == away_id and away_score > home_score:
            wins += 1
        total += 1
    return wins / total if total > 0 else 0.0


def get_head_to_head_matches(home_id, away_id):
    key = tuple(sorted([home_id, away_id]))
    if key in CACHE_HEAD2HEAD:
        return CACHE_HEAD2HEAD[key]
    url = f"https://volleyball.sportdevs.com/matches?or=(and(home_team_id.eq.{home_id},away_team_id.eq.{away_id}),and(home_team_id.eq.{away_id},away_team_id.eq.{home_id}))&order=specific_start_time.desc&limit=20"
    resp = requests.get(url, headers=headers)
    matches = resp.json()
    CACHE_HEAD2HEAD[key] = matches
    return matches


def compute_head_to_head_win_rate(matches, home_id):
    wins, total = 0, 0
    for match in matches:
        home_team = match["home_team_id"]
        away_team = match["away_team_id"]
        home_score = match.get("home_team_score", {}).get("display")
        away_score = match.get("away_team_score", {}).get("display")
        if home_score is None or away_score is None:
            continue
        if home_id == home_team and home_score > away_score:
            wins += 1
        elif home_id == away_team and away_score > home_score:
            wins += 1
        total += 1
    return wins / total if total > 0 else 0.0


def get_team_total_points(score_map):
    return sum(v for k, v in score_map.items() if k.startswith("period_") and isinstance(v, int))


def get_current_set_info(reason):
    try:
        return int(reason.split()[0].strip('stndrdth'))
    except:
        return 1


def format_set_scores(home_scores, away_scores, current_set):
    set_info = []
    for i in range(1, current_set + 1):
        home = home_scores.get(f'period_{i}', '?')
        away = away_scores.get(f'period_{i}', '?')
        set_info.append(f"Set {i}: {home}-{away}")
    return " | ".join(set_info)





def collect_snapshot_data():
    response = requests.get(MATCHES_URL, headers=headers, timeout=5)
    response.raise_for_status()
    matches = response.json()
    rows = []

    for match in matches:
        match_id = match["id"]
        home_id = match["home_team_id"]
        away_id = match["away_team_id"]
        home_score_map = match["home_team_score"]
        away_score_map = match["away_team_score"]

        home_sets = home_score_map.get("display", 0)
        away_sets = away_score_map.get("display", 0)

        home_total = get_team_total_points(home_score_map)
        away_total = get_team_total_points(away_score_map)

        score_diff = home_total - away_total
        set_diff = home_sets - away_sets

        match_status = match["status"]["reason"]
        current_set = get_current_set_info(match_status)

        home_current_score = home_score_map.get(f"period_{current_set}", '?')
        away_current_score = away_score_map.get(f"period_{current_set}", '?')        

        set_info = format_set_scores(home_score_map, away_score_map, current_set)

        duration = match.get("duration", 0)
        mins = duration // 60
        secs = duration % 60
        game_duration = f"{mins}m {secs}s"

        home_win_rate_last15 = compute_win_rate(get_team_last15_matches(home_id), home_id)
        away_win_rate_last15 = compute_win_rate(get_team_last15_matches(away_id), away_id)
        head2head_matches = get_head_to_head_matches(home_id, away_id)
        head_to_head_win_rate_home = compute_head_to_head_win_rate(head2head_matches, home_id)



        row = {
            "match_id": match_id,
            "timestamp": datetime.now(),
            "home_team_id": home_id,
            "away_team_id": away_id,
            "home_score_total": home_total,
            "away_score_total": away_total,
            "home_sets_won": home_sets,
            "away_sets_won": away_sets,
            "score_diff": score_diff,
            "set_diff": set_diff,
            "home_current_score": home_current_score,
            "away_current_score": away_current_score,
            "set_info": set_info,
            "game_duration": game_duration,
            "match_status": match_status,
            "home_win_rate_last15": home_win_rate_last15,
            "away_win_rate_last15": away_win_rate_last15,
            "head_to_head_win_rate_home": head_to_head_win_rate_home,

        }
        rows.append(row)

    return rows

def get_live_matches():
    """Recupera e ritorna l’elenco delle partite live."""
    resp = requests.get(MATCHES_URL, headers=headers)
    resp.raise_for_status()
    return resp.json()

def print_live_matches(matches):
    """Stampa in console le partite live date dalla lista matches."""
    if not matches:
        print("❌ Nessuna partita live in corso. Termino il programma.")
    else:
        print("🏐 Partite live in corso:")
        for m in matches:
            home = m["home_team"]["name"]
            away = m["away_team"]["name"]
            print(f" • ID {m['id']}: {home} vs {away}")

if __name__ == "__main__":
    LAST_SCORES = {}  # match_id → (home_current_score, away_current_score)
    while True:
        try:
            # 1) Recupera la lista delle live
            live_matches = get_live_matches()

            # 2) Stampa e, se vuota, esci
            print_live_matches(live_matches)
            if not live_matches:
                break  # esce dal while e termina il programma

            # 3) Raccogli snapshot solo dei match attivi
            snapshots = collect_snapshot_data()
            to_write = []
            for snap in snapshots:
                mid = snap["match_id"]
                curr = (snap["home_current_score"], snap["away_current_score"])
                if LAST_SCORES.get(mid) != curr:
                    to_write.append(snap)
                    LAST_SCORES[mid] = curr

            # 4) Scrivi su CSV se ci sono nuove righe
            if to_write:
                df = pd.DataFrame(to_write)
                df.to_csv(
                    "live_snapshots.csv",
                    mode='a',
                    index=False,
                    header=not os.path.exists("live_snapshots.csv")
                )
                print(f"✅ Snapshot aggiornato alle {datetime.now():%H:%M:%S} con {len(df)} nuove righe")
            else:
                print(f"⏭️ {datetime.now():%H:%M:%S} nessun cambiamento di punteggio")

        except Exception as e:
            print(f"❌ Errore nella raccolta dati: {e}")
            # a seconda di quanto vuoi essere robusto, potresti continuare o uscire:
            # break

        # Se arrivi qui, attendi il prossimo ciclo
        time.sleep(10)
