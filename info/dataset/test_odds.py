import requests
import time
import os
from datetime import datetime
import pandas as pd

API_KEY = "AymenURP9kWkgEatcBdcYA"
MATCHES_URL = "https://volleyball.sportdevs.com/matches?status_type=eq.live"

headers = {
    'Accept': 'application/json',
    "Authorization": f"Bearer {API_KEY}"
}

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

def extract_odds_features(match):
    odds_list = match.get("periods", [{}])[0].get("odds", [])
    if not odds_list:
        return {
            "home_odds": None,
            "away_odds": None,
            "home_prob": None,
            "away_prob": None,
            "odds_diff": None,
            "prob_diff": None,
            "payout": None
        }

    selected_odds = odds_list[0]
    home_odds = selected_odds.get("home")
    away_odds = selected_odds.get("away")

    try:
        home_prob = round(1 / home_odds, 4)
        away_prob = round(1 / away_odds, 4)
        odds_diff = round(away_odds - home_odds, 4)
        prob_diff = round(home_prob - away_prob, 4)
        payout = round(100 * (home_prob + away_prob), 2)
    except (ZeroDivisionError, TypeError):
        home_prob = away_prob = odds_diff = prob_diff = payout = None

    return {
        "home_odds": home_odds,
        "away_odds": away_odds,
        "home_prob": home_prob,
        "away_prob": away_prob,
        "odds_diff": odds_diff,
        "prob_diff": prob_diff,
        "payout": payout
    }

while True:
    try:
        response = requests.get(MATCHES_URL, headers=headers, timeout=5)
        response.raise_for_status()
        matches = response.json()

        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\nUltimo aggiornamento: {datetime.now().strftime('%H:%M:%S')}\n")

        rows = []

        for match in matches:
            match_id = match["id"]
            home_id = match["home_team_id"]
            away_id = match["away_team_id"]
            home_name = match["home_team_name"]
            away_name = match["away_team_name"]

            home_score_map = match["home_team_score"]
            away_score_map = match["away_team_score"]

            home_sets = home_score_map.get("sets_won", 0)
            away_sets = away_score_map.get("sets_won", 0)

            home_total = get_team_total_points(home_score_map)
            away_total = get_team_total_points(away_score_map)

            score_diff = home_total - away_total
            set_diff = home_sets - away_sets

            match_status = match["status"]["reason"]
            current_set = get_current_set_info(match_status)

            home_current_score = home_score_map.get("current", '?')
            away_current_score = away_score_map.get("current", '?')

            set_info = format_set_scores(home_score_map, away_score_map, current_set)

            duration = match.get("duration", 0)
            mins = duration // 60
            secs = duration % 60
            game_duration = f"{mins}m {secs}s"

            odds_features = extract_odds_features(match)

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
                **odds_features
            }

            rows.append(row)

            print(f"📊 {home_name} vs {away_name} | Totale punti: {home_total}-{away_total} | Set: {home_sets}-{away_sets}")
            print(f"  🏠 Punteggio attuale: {home_current_score} | ✈️ Punteggio attuale: {away_current_score}")
            print(f"  🎯 Set: {set_info}")
            print(f"  🔄 Stato: {match_status} | ⏱ Tempo: {game_duration}")
            print(f"  💸 Odds: home {odds_features['home_odds']} | away {odds_features['away_odds']}")
            print(f"  📉 Probabilità: home {odds_features['home_prob']} | away {odds_features['away_prob']}")
            print("-"*60)

        df = pd.DataFrame(rows)
        print("\n🧾 DataFrame attuale:")
        print(df)

    except Exception as e:
        print(f"❌ Errore nella richiesta API o nel parsing: {e}")

    time.sleep(10)
