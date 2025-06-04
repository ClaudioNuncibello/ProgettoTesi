#!/usr/bin/env python3
"""
volley_predict_local.py

Questo script allena un modello LogisticRegression offline (usando pandas e scikit-learn),
su dati di training (trainer.csv) e poi applica il modello a uno snapshot (snapshot.csv),
aggiungendo alla seconda tabella la colonna 'predicted_win' con la probabilità di vittoria del team di casa.

Vantaggi di LogisticRegression:
- Se il vettore delle feature è 0 (“neutro”), la predizione sarà 0.5 di default.
- Con feature centrate, non c’è più quel bias iniziale che faceva partire da 1.0 o 0.9.

Esempio di utilizzo:
    python3 volley_predict_local.py \
        --trainer trainer.csv \
        --snapshot snapshot.csv \
        --output snapshot_with_pred.csv
"""

import re
import argparse
import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# -------------------------------------------------------------------
# 1) Funzione per parsare "148m 58s" → secondi (float)
# -------------------------------------------------------------------
def parse_duration(s: str) -> float:
    if pd.isna(s):
        return np.nan
    m = re.search(r"(\d+)m", s)
    sec = re.search(r"(\d+)s", s)
    mins = float(m.group(1)) if m else 0.0
    secs = float(sec.group(1)) if sec else 0.0
    return mins * 60.0 + secs

# -------------------------------------------------------------------
# 2) Estrai current_set_number da 'match_status'
#    (es. "1st set", "2nd set", "3rd set", "3rd set ended")
# -------------------------------------------------------------------
def compute_current_set_number(match_status: str) -> int:
    if not isinstance(match_status, str):
        return 1
    s = match_status.lower().strip()
    # Se comincia con "1", "2" o "3"
    if s.startswith("1"):
        return 1
    if s.startswith("2"):
        return 2
    if s.startswith("3"):
        return 3
    # Fallback su "1st", "2nd", "3rd"
    if "1st" in s:
        return 1
    if "2nd" in s:
        return 2
    if "3rd" in s:
        return 3
    return 1

# -------------------------------------------------------------------
# 3) Estrai differenza dell'ultimo set da 'set_info'
#    (es. "Set 1: 25-14 | Set 2: 18-16 | Set 3: 8-15" → 8-15 = -7)
# -------------------------------------------------------------------
def extract_current_set_diff(set_info: str, overall_diff: float) -> float:
    if not isinstance(set_info, str):
        return overall_diff
    parts = set_info.split("|")
    last = parts[-1].strip()
    if ":" not in last:
        return overall_diff
    try:
        score_part = last.split(":")[1].strip()  # es. "8-15"
        a, b = score_part.split("-")
        return float(a) - float(b)
    except:
        return overall_diff

# -------------------------------------------------------------------
# 4) Calcola set_importance (0.5 o 1.0)
#     - 1.0 se vincere il set corrente chiude il match
#     - 0.5 altrimenti
# -------------------------------------------------------------------
def compute_set_importance(home_sets_won: float, away_sets_won: float, current_set_number: int) -> float:
    hs, aw, cs = home_sets_won, away_sets_won, current_set_number
    # 3° set con 1–1 nei set ⇒ chiude
    if cs == 3 and hs == 1 and aw == 1:
        return 1.0
    # 2° set con uno dei due già a 1–0 nei set ⇒ chiude
    if cs == 2 and ((hs == 1 and aw == 0) or (aw == 1 and hs == 0)):
        return 1.0
    return 0.5

# -------------------------------------------------------------------
# 5) Calcola flag di momento critico per home/away
#    - flag_3set_severo_home: 3° set e svantaggio in set_diff_current ≤ –3
#    - flag_3set_severo_away: 3° set e svantaggio in set_diff_current ≥ +3
#    - flag_critico_base_home: (punteggio ≥20 e diff complessiva ≤–2)
#    - flag_critico_base_away: (punteggio ≥20 e diff complessiva ≥+2)
# -------------------------------------------------------------------
def compute_flags(df: pd.DataFrame) -> pd.DataFrame:
    df["flag_3set_severo_home"] = (
        (df["current_set_number"] == 3) &
        (df["set_diff_current"] <= -3)
    ).astype(int)
    df["flag_3set_severo_away"] = (
        (df["current_set_number"] == 3) &
        (df["set_diff_current"] >= 3)
    ).astype(int)
    df["flag_critico_base_home"] = (
        ((df["home_current_score"] >= 20) | (df["away_current_score"] >= 20)) &
        (df["score_diff"] <= -2)
    ).astype(int)
    df["flag_critico_base_away"] = (
        ((df["home_current_score"] >= 20) | (df["away_current_score"] >= 20)) &
        (df["score_diff"] >= 2)
    ).astype(int)
    return df

# -------------------------------------------------------------------
# 6) Win rate aggiustati per home / away
#    - Penalità severa: 3° set e set_diff_current ≤ –3  ⇒ base × 0.05
#    - Penalità “critica”: punteggio ≥20 e diff complessiva ≤ –2 ⇒ base × 0.25
#    - Moltiplichiamo poi per set_importance
# -------------------------------------------------------------------
def compute_home_win_rate_adj(row) -> float:
    base = row["home_win_rate_last5"]
    sd = row["set_diff_current"]
    cs = row["current_set_number"]
    if cs == 3 and sd <= -3:
        adj = base * 0.05
    elif ((row["home_current_score"] >= 20) or (row["away_current_score"] >= 20)) and (row["score_diff"] <= -2):
        adj = base * 0.25
    else:
        adj = base
    return adj * row["set_importance"]

def compute_away_win_rate_adj(row) -> float:
    base = row["away_win_rate_last5"]
    sd = row["set_diff_current"]
    cs = row["current_set_number"]
    if cs == 3 and sd >= 3:
        adj = base * 0.05
    elif ((row["home_current_score"] >= 20) or (row["away_current_score"] >= 20)) and (row["score_diff"] >= 2):
        adj = base * 0.25
    else:
        adj = base
    return adj * row["set_importance"]

# -------------------------------------------------------------------
# 7) Funzione che aggiunge tutte le feature avanzate
# -------------------------------------------------------------------
def add_advanced_features(df: pd.DataFrame) -> pd.DataFrame:
    # 7.1) set_diff_current
    df["set_diff_current"] = df.apply(
        lambda row: extract_current_set_diff(row["set_info"], row["score_diff"]),
        axis=1
    )

    # 7.2) current_set_number
    df["current_set_number"] = df["match_status"] \
        .map(compute_current_set_number) \
        .astype(int)

    # 7.3) set_importance
    df["set_importance"] = df.apply(
        lambda row: compute_set_importance(
            row["home_sets_won"],
            row["away_sets_won"],
            row["current_set_number"]
        ),
        axis=1
    )

    # 7.4) flag di momento critico
    df = compute_flags(df)

    # 7.5) home_win_rate_adj e away_win_rate_adj
    df["home_win_rate_adj"] = df.apply(compute_home_win_rate_adj, axis=1)
    df["away_win_rate_adj"] = df.apply(compute_away_win_rate_adj, axis=1)

    # 7.6) win_rate_diff
    df["win_rate_diff"] = df["home_win_rate_adj"] - df["away_win_rate_adj"]

    return df

# -------------------------------------------------------------------
# 8) Funzione principale: main()
# -------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Allena un modello RandomForest offline e predice sullo snapshot"
    )
    parser.add_argument(
        "--trainer", "-t",
        default="/Users/claudio/Documents/GitHub/ProgettoTesi/scripts/trainer/live_snapshots_target.csv",
        help="Percorso al CSV di training (contiene anche la colonna target_win)"
    )
    parser.add_argument(
        "--snapshot", "-s",
        default="/Users/claudio/Documents/GitHub/ProgettoTesi/scripts/simulated_snapshots.csv",
        help="Percorso al CSV contenente gli snapshot (senza target_win)"
    )
    parser.add_argument(
        "--output", "-o",
        default="/Users/claudio/Documents/GitHub/ProgettoTesi/scripts/predicted_snapshots.csv",
        help="Percorso del CSV di output con la colonna predicted_win"
    )
    args = parser.parse_args()

    # -------------------------------------------------------------------
    # 9) Carica il CSV di training con pandas
    # -------------------------------------------------------------------
    df_train = pd.read_csv(
        args.trainer,
        dtype={
            "match_id": int,
            "timestamp": str,
            "home_team_id": int,
            "away_team_id": int,
            "home_score_total": float,
            "away_score_total": float,
            "home_sets_won": float,
            "away_sets_won": float,
            "score_diff": float,
            "set_diff": float,
            "home_current_score": float,
            "away_current_score": float,
            "set_info": str,
            "game_duration": str,
            "match_status": str,
            "home_win_rate_last5": float,
            "away_win_rate_last5": float,
            "head_to_head_win_rate_home": float,
            "target_win": int,
        }
    )

    # 9.1) parse_duration su 'game_duration'
    df_train["game_duration"] = df_train["game_duration"].map(parse_duration)

    # 9.2) Rimuove righe senza target
    df_train = df_train[df_train["target_win"].notna()]

    # 9.3) Aggiungi tutte le feature avanzate
    df_train = add_advanced_features(df_train)

    # -------------------------------------------------------------------
    # 10) Definisci feature numeriche e categoriali (inclusi i nuovi)
    # -------------------------------------------------------------------
    num_cols = [
        "home_score_total", "away_score_total",
        "home_sets_won", "away_sets_won",
        "score_diff", "set_diff",
        "home_current_score", "away_current_score",
        "game_duration",
        "home_win_rate_last5", "away_win_rate_last5",
        "head_to_head_win_rate_home",
        # NUOVE FEATURE
        "set_diff_current", "current_set_number", "set_importance",
        "home_win_rate_adj", "away_win_rate_adj", "win_rate_diff"
    ]
    cat_cols = ["home_team_id", "away_team_id"]

    X_train = df_train[num_cols + cat_cols].copy()
    y_train = df_train["target_win"].astype(int).copy()

    # -------------------------------------------------------------------
    # 11) Costruisci la pipeline di preprocessing + LogisticRegression
    #
    #  - SimpleImputer(strategy="median") sulle numeriche
    #  - OneHotEncoder(…) sulle categoriali
    #  - StandardScaler() sulle numeriche centrate (fa sì che valori “neutri” diventino esattamente 0)
    #  - LogisticRegression(C=1.0) come classificatore
    # -------------------------------------------------------------------
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())  # centra e scala; uno “stato neutro” = 0
    ])
    categorical_transformer = OneHotEncoder(handle_unknown="ignore", sparse_output=False)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, num_cols),
            ("cat", categorical_transformer, cat_cols),
        ],
        remainder="drop"
    )

    clf = Pipeline(steps=[
        ("preproc", preprocessor),
        ("lr", LogisticRegression(penalty="l2", C=1.0, max_iter=1000, random_state=42))
    ])

    # 11.1) Fit sul training set
    clf.fit(X_train, y_train)

    # -------------------------------------------------------------------
    # 12) Carica il CSV di snapshot con pandas
    # -------------------------------------------------------------------
    df_snap = pd.read_csv(
        args.snapshot,
        dtype={
            "match_id": int,
            "timestamp": str,
            "home_team_id": int,
            "away_team_id": int,
            "home_score_total": float,
            "away_score_total": float,
            "home_sets_won": float,
            "away_sets_won": float,
            "score_diff": float,
            "set_diff": float,
            "home_current_score": float,
            "away_current_score": float,
            "set_info": str,
            "game_duration": str,
            "match_status": str,
            "home_win_rate_last5": float,
            "away_win_rate_last5": float,
            "head_to_head_win_rate_home": float,
        }
    )

    # 12.1) parse_duration su 'game_duration'
    df_snap["game_duration"] = df_snap["game_duration"].map(parse_duration)

    # 12.2) Aggiungi le stesse feature avanzate
    df_snap = add_advanced_features(df_snap)

    # -------------------------------------------------------------------
    # 13) Prepara X_snap e predici
    # -------------------------------------------------------------------
    X_snap = df_snap[num_cols + cat_cols].copy()
    probs = clf.predict_proba(X_snap)[:, 1]
    df_snap["predicted_win"] = probs

    # -------------------------------------------------------------------
    # 14) Salva il risultato in CSV di output
    # -------------------------------------------------------------------
    df_snap.to_csv(args.output, index=False)
    print(f"✅ Predizioni salvate in: {args.output}")

if __name__ == "__main__":
    main()
