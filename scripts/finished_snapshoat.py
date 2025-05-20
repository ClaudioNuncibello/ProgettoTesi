import requests
import os
import pandas as pd
from datetime import datetime

API_KEY = "AymenURP9kWkgEatcBdcYA"
BASE_URL = "https://volleyball.sportdevs.com/matches"
FINISHED_MATCHES_PARAMS = {
    'season_id': 'eq.17700',
    'limit': 10,
    'status_type': 'eq.finished'
}

headers = {
    'Accept': 'application/json',
    'Authorization': f"Bearer {API_KEY}"
}

# Caches
CACHE_TEAM_MATCHES = {}
CACHE_HEAD2HEAD = {}


def get_matches_finished():
    """Recupera tutte le partite concluse"""
    resp = requests.get(BASE_URL, headers=headers, params=FINISHED_MATCHES_PARAMS)
    resp.raise_for_status()
    return resp.json()


def get_team_last5_before(team_id: int, cutoff: str):
    """Recupera ultime 5 partite di team_id con start_time < cutoff, gestendo errori 500"""
    key = (team_id, cutoff)
    if key in CACHE_TEAM_MATCHES:
        return CACHE_TEAM_MATCHES[key]
    params = {
        'or': f'(home_team_id.eq.{team_id},away_team_id.eq.{team_id})',
        'order': 'specific_start_time.desc',
        'specific_start_time': f'lt.{cutoff}',
        'limit': 5
    }
    try:
        resp = requests.get(BASE_URL, headers=headers, params=params)
        resp.raise_for_status()
        matches = resp.json()
    except requests.exceptions.HTTPError as e:
        print(f"⚠️ Errore fetching last5 for team {team_id} before {cutoff}: {e}")
        matches = []
    CACHE_TEAM_MATCHES[key] = matches
    return matches


def get_head2head_before(home_id: int, away_id: int, cutoff: str):
    """Recupera head-to-head fino a cutoff, gestendo errori 500"""
    # caching key without mixing types
    key = (min(home_id, away_id), max(home_id, away_id), cutoff)
    if key in CACHE_HEAD2HEAD:
        return CACHE_HEAD2HEAD[key]
    params = {
        'or': f'(and(home_team_id.eq.{home_id},away_team_id.eq.{away_id}),' \
              f'and(home_team_id.eq.{away_id},away_team_id.eq.{home_id}))',
        'order': 'specific_start_time.desc',
        'specific_start_time': f'lt.{cutoff}',
        'limit': 20
    }
    try:
        resp = requests.get(BASE_URL, headers=headers, params=params)
        resp.raise_for_status()
        matches = resp.json()
    except requests.exceptions.HTTPError as e:
        print(f"⚠️ Errore fetching h2h for {home_id} vs {away_id} before {cutoff}: {e}")
        matches = []
    CACHE_HEAD2HEAD[key] = matches
    return matches


def compute_win_rate(matches, team_id: int) -> float:
    wins = total = 0
    for m in matches:
        hs = m.get("home_team_score", {}).get("display")
        aw = m.get("away_team_score", {}).get("display")
        if hs is None or aw is None:
            continue
        if team_id == m["home_team_id"] and hs > aw:
            wins += 1
        elif team_id == m["away_team_id"] and aw > hs:
            wins += 1
        total += 1
    return wins / total if total else 0.0


def get_total_points(score_map: dict) -> int:
    return sum(v for k, v in score_map.items() if k.startswith("period_") and isinstance(v, int))


def get_current_set_info(periods: dict) -> int:
    nums = [int(k.split('_')[1]) for k in periods.keys() if k.startswith("period_")]
    return max(nums) if nums else 1


def format_sets(home_scores: dict, away_scores: dict, n_sets: int) -> str:
    parts = []
    for i in range(1, n_sets + 1):
        h = home_scores.get(f"period_{i}", "?")
        a = away_scores.get(f"period_{i}", "?")
        parts.append(f"Set {i}: {h}-{a}")
    return " | ".join(parts)


def collect_finished_snapshot():
    finished = get_matches_finished()
    rows = []
    for m in finished:
        start = m.get("specific_start_time")
        cutoff = start.split('Z')[0]
        home_id = m["home_team_id"]
        away_id = m["away_team_id"]

        # punteggi totali e set
        home_map = m.get("home_team_score", {})
        away_map = m.get("away_team_score", {})
        home_total = get_total_points(home_map)
        away_total = get_total_points(away_map)
        home_sets = home_map.get("display", 0)
        away_sets = away_map.get("display", 0)
        score_diff = home_total - away_total
        set_diff = home_sets - away_sets

        # info set
        n_sets = get_current_set_info(home_map)
        home_cur = home_map.get(f"period_{n_sets}", "?")
        away_cur = away_map.get(f"period_{n_sets}", "?")
        set_info = format_sets(home_map, away_map, n_sets)

        # durata
        duration = m.get("duration", 0)
        mins, secs = divmod(duration, 60)
        game_duration = f"{mins}m {secs}s"

        # win rates pre-match
        hr5_h = compute_win_rate(get_team_last5_before(home_id, cutoff), home_id)
        hr5_a = compute_win_rate(get_team_last5_before(away_id, cutoff), away_id)
        h2h = compute_win_rate(get_head2head_before(home_id, away_id, cutoff), home_id)

        rows.append({
            "match_id": m["id"],
            "timestamp": datetime.now(),
            "home_team_id": home_id,
            "away_team_id": away_id,
            "home_score_total": home_total,
            "away_score_total": away_total,
            "home_sets_won": home_sets,
            "away_sets_won": away_sets,
            "score_diff": score_diff,
            "set_diff": set_diff,
            "home_current_score": home_cur,
            "away_current_score": away_cur,
            "set_info": set_info,
            "game_duration": game_duration,
            "match_status": m.get("status", {}).get("reason", "finished"),
            "home_win_rate_last5": hr5_h,
            "away_win_rate_last5": hr5_a,
            "head_to_head_win_rate_home": h2h,
        })

    df = pd.DataFrame(rows)
    out = "/Users/claudio/Documents/GitHub/ProgettoTesi/scripts"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Saved {len(df)} finished snapshots to {out}")


if __name__ == "__main__":
    collect_finished_snapshot()
