import pandas as pd
import numpy as np
import requests
from tqdm import tqdm

# --- CONFIGURAZIONE ---
API_KEY     = "AymenURP9kWkgEatcBdcYA"
MATCHES_URL = "https://volleyball.sportdevs.com/matches?id=eq.{match_id}"
HEADERS     = {
    'Accept': 'application/json',
    'Authorization': f"Bearer {API_KEY}"
}
TIMEOUT     = 10  # secondi per la chiamata HTTP
CSV_PATH    = '/Users/claudio/Documents/GitHub/ProgettoTesi/scripts/live_snapshots.csv'
OUT_PATH    = '/Users/claudio/Documents/GitHub/ProgettoTesi/scripts/live_snapshots_target.csv'

# --- 1) Leggi tutti gli snapshot ---
df = pd.read_csv(CSV_PATH)
print(f"Caricati {len(df)} snapshot da {CSV_PATH}")

# --- 2) Prepara mappe per status_type e set_vinti (campo "display") ---
status_map    = {}
home_sets_map = {}
away_sets_map = {}

for mid in tqdm(df['match_id'].unique(), desc="Fetching match info"):
    url = MATCHES_URL.format(match_id=mid)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        print(data)
        
        if data:
            rec    = data[0]
            status = rec.get('status_type')

            # Estrai display da dict home_team_score / away_team_score
            home_score_map = rec.get('home_team_score', {})
            away_score_map = rec.get('away_team_score', {})
            home_sets = home_score_map.get('display', 0)
            away_sets = away_score_map.get('display', 0)
        else:
            status, home_sets, away_sets = None, np.nan, np.nan

    except Exception as e:
        print(f"Warning: errore match_id={mid}: {e}")
        status, home_sets, away_sets = None, np.nan, np.nan

    status_map[mid]    = status
    home_sets_map[mid] = home_sets
    away_sets_map[mid] = away_sets

# --- 3) Aggiungi la colonna target_win direttamente negli snapshot ---
def compute_target(mid):
    st = status_map.get(mid)
    if st != 'finished':
        return np.nan
    return 1 if home_sets_map[mid] > away_sets_map[mid] else 0

df['target_win'] = df['match_id'].apply(compute_target)

# --- 4) Salva il CSV con la sola nuova etichetta ---
df.to_csv(OUT_PATH, index=False)
print(f"File con target_win salvato come {OUT_PATH}")
