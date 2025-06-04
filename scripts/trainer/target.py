import pandas as pd
import numpy as np
import requests
import os
from tqdm import tqdm

# --- CONFIGURAZIONE ---
API_KEY     = "Zc6NKDUI70eCDcwwgxj_kw"
MATCHES_URL = "https://volleyball.sportdevs.com/matches?id=eq.{match_id}"
HEADERS     = {
    'Accept': 'application/json',
    'Authorization': f"Bearer {API_KEY}"
}
TIMEOUT     = 10  # secondi per la chiamata HTTP

CSV_PATH    = '/Users/claudio/Documents/GitHub/ProgettoTesi/scripts/live_snapshots.csv'
OUT_PATH    = '/Users/claudio/Documents/GitHub/ProgettoTesi/scripts/trainer/live_snapshots_target.csv'

# --- 1) Leggi tutti gli snapshot, uniforma match_id ---
df = pd.read_csv(CSV_PATH)
print(f"Caricati {len(df)} snapshot da {CSV_PATH}")
df['match_id'] = df['match_id'].astype(int)

# --- 2) Recupera info match dall'API ---
unique_ids = df['match_id'].unique().tolist()
print(f"Trovati {len(unique_ids)} match_id unici.")

matches_info = {
    'match_id': [],
    'status_type': [],
    'home_sets': [],
    'away_sets': []
}

for mid in tqdm(unique_ids, desc="Fetching match info"):
    url = MATCHES_URL.format(match_id=mid)
    status, home_sets, away_sets = None, np.nan, np.nan

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        if data and len(data) > 0:
            rec = data[0]
            status = rec.get('status_type')

            home_score_map = rec.get('home_team_score', {})
            away_score_map = rec.get('away_team_score', {})
            home_sets = home_score_map.get('display', 0)
            away_sets = away_score_map.get('display', 0)
        else:
            status, home_sets, away_sets = None, np.nan, np.nan

    except Exception as e:
        print(f"Warning: errore con match_id={mid}: {e}")
        status, home_sets, away_sets = None, np.nan, np.nan

    matches_info['match_id'].append(mid)
    matches_info['status_type'].append(status)
    matches_info['home_sets'].append(home_sets)
    matches_info['away_sets'].append(away_sets)

df_matches = pd.DataFrame(matches_info)
print("Info match recuperate:")
print(df_matches.head())

# --- 3) Unisci e calcola target_win ---
df_merged = df.merge(df_matches, on='match_id', how='left')

def compute_target_win(row):
    if row['status_type'] != 'finished':
        return np.nan
    return 1 if row['home_sets'] > row['away_sets'] else 0

df_merged['target_win'] = df_merged.apply(compute_target_win, axis=1)

# Rimuovi le colonne intermedie lasciando solo quelle originali + target_win
to_drop = ['status_type', 'home_sets', 'away_sets']
df_final = df_merged.drop(columns=to_drop)

# --- 4) Salva il CSV con solo target_win aggiunto ---
if os.path.exists(OUT_PATH):
    os.remove(OUT_PATH)

df_final.to_csv(OUT_PATH, index=False)
print(f"File con target_win salvato come {OUT_PATH}")
