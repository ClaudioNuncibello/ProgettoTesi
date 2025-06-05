import pandas as pd
import numpy as np
import requests
import os
from tqdm import tqdm

# --- CONFIGURAZIONE ---
API_KEY = "2SRC4Sh4lkukveijWwruFw"
MATCHES_URL = "https://volleyball.sportdevs.com/matches?id=eq.{match_id}"
HEADERS     = {
    'Accept': 'application/json',
    'Authorization': f"Bearer {API_KEY}"
}
TIMEOUT     = 10  # secondi per la chiamata HTTP

CSV_PATH   = '/Users/claudio/Documents/GitHub/ProgettoTesi/scripts/live_snapshots.csv'
CACHE_PATH = '/Users/claudio/Documents/GitHub/ProgettoTesi/scripts/trainer/matches_cache.txt'
OUT_PATH   = '/Users/claudio/Documents/GitHub/ProgettoTesi/scripts/trainer/trainer_model.csv'

# --- 1) Leggi tutti gli snapshot e uniforma match_id ---
df = pd.read_csv(CSV_PATH)
print(f"Caricati {len(df)} snapshot da {CSV_PATH}")
df['match_id'] = df['match_id'].astype(int)

# --- 2) Prepara il file di cache (TXT) con i match_id già processati ---
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH, 'r') as f:
        cached_ids = {int(line.strip()) for line in f if line.strip()}
    print(f"Caricata cache esistente con {len(cached_ids)} match_id (da {CACHE_PATH})")
else:
    cached_ids = set()
    print(f"Nessuna cache trovata. Verrà creato un nuovo file {CACHE_PATH}")

# --- 3) Determina quali match_id servono ancora da chiamare via API ---
unique_ids = set(df['match_id'].tolist())
print(f"Trovati {len(unique_ids)} match_id unici nello snapshot")

to_fetch_ids = sorted(unique_ids - cached_ids)
print(f"Di questi, {len(to_fetch_ids)} non presenti in cache e verranno recuperati da API")

# --- 4) Recupera info match dall'API solo per i nuovi match_id ---
matches_info_new = {
    'match_id': [],
    'status_type': [],
    'home_sets': [],
    'away_sets': []
}

for mid in tqdm(to_fetch_ids, desc="Fetching match info"):
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

    matches_info_new['match_id'].append(mid)
    matches_info_new['status_type'].append(status)
    matches_info_new['home_sets'].append(home_sets)
    matches_info_new['away_sets'].append(away_sets)

# Se non ci sono nuovi match, fermiamo qui
if len(matches_info_new['match_id']) == 0:
    print("Nessun nuovo match da recuperare; esco.")
    exit(0)

# --- 5) Costruisci DataFrame con le info dei nuovi match ---
df_new = pd.DataFrame(matches_info_new)

# --- 6) Seleziona solo le righe snapshot relative ai nuovi match_id e unisci le info ---
df_snap_new = df[df['match_id'].isin(to_fetch_ids)].copy()
df_merged_new = df_snap_new.merge(df_new, on='match_id', how='left')

def compute_target_win(row):
    if row['status_type'] != 'finished':
        return np.nan
    return 1 if row['home_sets'] > row['away_sets'] else 0

df_merged_new['target_win'] = df_merged_new.apply(compute_target_win, axis=1)

# Rimuovi le colonne intermedie lasciando solo quelle originali + target_win
to_drop = ['status_type', 'home_sets', 'away_sets']
df_final_new = df_merged_new.drop(columns=to_drop)

# --- 7) Scrivi/append al CSV di output (trainer_model.csv) ---
if os.path.exists(OUT_PATH):
    # In questo approccio, siamo sicuri di non avere duplicati perché
    # stiamo aggiungendo solo snapshot di nuovi match_id.
    df_final_new.to_csv(OUT_PATH, mode='a', index=False, header=False)
    print(f"Aggiunte {len(df_final_new)} righe nuove in append a {OUT_PATH}")
else:
    df_final_new.to_csv(OUT_PATH, index=False)
    print(f"File con target_win creato ex novo come {OUT_PATH} ({len(df_final_new)} righe)")

# --- 8) Aggiorna la cache TXT con i nuovi match_id ---
with open(CACHE_PATH, 'a') as f:
    for mid in to_fetch_ids:
        f.write(f"{mid}\n")
print(f"Aggiunti {len(to_fetch_ids)} match_id a {CACHE_PATH}")
