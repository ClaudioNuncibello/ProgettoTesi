#!/usr/bin/env python3
import pandas as pd
import numpy as np
import requests
import os
from tqdm import tqdm

# --- CONFIGURAZIONE ---
API_KEY    = "2SRC4Sh4lkukveijWwruFw"
MATCHES_URL= "https://volleyball.sportdevs.com/matches?id=eq.{match_id}"
HEADERS    = {
    'Accept': 'application/json',
    'Authorization': f"Bearer {API_KEY}"
}
TIMEOUT    = 10  # secondi per la chiamata HTTP

CSV_PATH   = '/Users/claudio/Documents/GitHub/ProgettoTesi/Producer/live_snapshots.csv'
CACHE_PATH = '/Users/claudio/Documents/GitHub/ProgettoTesi/scripts/trainer/matches_cache.txt'
OUT_PATH   = '/Users/claudio/Documents/GitHub/ProgettoTesi/spark/data/trainer_model.csv'

# --- 1) Leggi tutti gli snapshot e uniforma match_id ---
print(f"Caricamento {CSV_PATH} …")
df = pd.read_csv(
    CSV_PATH,
    engine="python",
    on_bad_lines="skip",    # salta le righe malformate
    sep=",",                # o cambia a secondo del tuo CSV
    quotechar='"',
    dtype=str              # leggi tutto come stringa, poi converti
)
print(f"→ snapshot caricati: {len(df)} righe (righe mal formate saltate)")

df = df.rename(columns=str.strip)         # rimuove spazi involontari nei nomi
df['match_id'] = df['match_id'].astype(int)

# --- 2) Carica cache match già processati ---
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH, 'r') as f:
        cached_ids = {int(line.strip()) for line in f if line.strip()}
    print(f"→ cache caricata: {len(cached_ids)} match_id")
else:
    cached_ids = set()
    print(f"→ nessuna cache trovata, ne verrà creata una nuova")

# --- 3) Trova match_id da fetchare ---
unique_ids   = set(df['match_id'])
to_fetch_ids = sorted(unique_ids - cached_ids)
print(f"→ {len(unique_ids)} match unici, di cui {len(to_fetch_ids)} da chiamare")

# --- 4) Fetch info solo sui nuovi match_id ---
matches_info = {'match_id':[], 'status_type':[], 'home_sets':[], 'away_sets':[]}
for mid in tqdm(to_fetch_ids, desc="Fetching match info"):
    try:
        resp = requests.get(MATCHES_URL.format(match_id=mid), headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if data:
            rec = data[0]
            status = rec.get('status_type')
            home_sets = rec.get('home_team_score',{}).get('display', np.nan)
            away_sets = rec.get('away_team_score',{}).get('display', np.nan)
        else:
            status, home_sets, away_sets = None, np.nan, np.nan
    except Exception as e:
        print(f"⚠️ Errore match_id={mid}: {e}")
        status, home_sets, away_sets = None, np.nan, np.nan

    matches_info['match_id'].append(mid)
    matches_info['status_type'].append(status)
    matches_info['home_sets'].append(home_sets)
    matches_info['away_sets'].append(away_sets)

# --- 5) Se non ci sono nuovi, esci ---
if not matches_info['match_id']:
    print("Nessun nuovo match da recuperare; esco.")
    exit(0)

# --- 6) Unisci snapshot + info match ---
df_new     = pd.DataFrame(matches_info)
df_snap    = df[df['match_id'].isin(to_fetch_ids)].copy()
df_merged  = df_snap.merge(df_new, on='match_id', how='left')

def compute_target_win(row):
    if row['status_type'] != 'finished':
        return np.nan
    return 1 if row['home_sets'] > row['away_sets'] else 0

df_merged['target_win'] = df_merged.apply(compute_target_win, axis=1)

# togliamo colonne intermedie
df_final = df_merged.drop(columns=['status_type','home_sets','away_sets'])

# --- 7) Append o crea il CSV di training ---
header = not os.path.exists(OUT_PATH)
df_final.to_csv(OUT_PATH, mode='a', index=False, header=header)
print(f"→ salvate {len(df_final)} righe in '{OUT_PATH}' (header={header})")

# --- 8) Aggiorna cache ---
with open(CACHE_PATH, 'a') as f:
    for mid in to_fetch_ids:
        f.write(f"{mid}\n")
print(f"→ aggiornati {len(to_fetch_ids)} match_id in cache '{CACHE_PATH}'")
