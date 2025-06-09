#!/usr/bin/env python3
"""
train_model.py

Script per l'addestramento offline di un modello predittivo (LogisticRegression)
basato su snapshot di partite di pallavolo. Il modello viene serializzato
in formato joblib e potrà essere successivamente utilizzato da Spark.
"""

import re
import pandas as pd
import numpy as np
import joblib

from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# ------------------ Funzioni di feature engineering ------------------

def parse_duration(s: str) -> float:
    if pd.isna(s):
        return np.nan
    m = re.search(r"(\d+)m", s)
    sec = re.search(r"(\d+)s", s)
    mins = float(m.group(1)) if m else 0.0
    secs = float(sec.group(1)) if sec else 0.0
    return mins * 60.0 + secs

def compute_current_set_number(match_status: str) -> int:
    if not isinstance(match_status, str):
        return 1
    s = match_status.lower().strip()
    if s.startswith("1"): return 1
    if s.startswith("2"): return 2
    if s.startswith("3"): return 3
    if "1st" in s: return 1
    if "2nd" in s: return 2
    if "3rd" in s: return 3
    return 1

def extract_current_set_diff(set_info: str, overall_diff: float) -> float:
    if not isinstance(set_info, str):
        return overall_diff
    parts = set_info.split("|")
    last = parts[-1].strip()
    if ":" not in last:
        return overall_diff
    try:
        score_part = last.split(":")[1].strip()
        a, b = score_part.split("-")
        return float(a) - float(b)
    except:
        return overall_diff

def compute_set_importance(hs: float, aw: float, cs: int) -> float:
    if cs == 3 and hs == 1 and aw == 1:
        return 1.0
    if cs == 2 and ((hs == 1 and aw == 0) or (aw == 1 and hs == 0)):
        return 1.0
    return 0.5

def compute_flags(df: pd.DataFrame) -> pd.DataFrame:
    df["flag_3set_severo_home"] = (
        (df["current_set_number"] == 3) & (df["set_diff_current"] <= -3)
    ).astype(int)
    df["flag_3set_severo_away"] = (
        (df["current_set_number"] == 3) & (df["set_diff_current"] >= 3)
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

def add_advanced_features(df: pd.DataFrame) -> pd.DataFrame:
    df["set_diff_current"] = df.apply(
        lambda row: extract_current_set_diff(row["set_info"], row["score_diff"]), axis=1
    )
    df["current_set_number"] = df["match_status"] \
        .map(compute_current_set_number).astype(int)
    df["set_importance"] = df.apply(
        lambda row: compute_set_importance(
            row["home_sets_won"],
            row["away_sets_won"],
            row["current_set_number"]
        ),
        axis=1
    )
    df = compute_flags(df)
    df["home_win_rate_adj"] = df.apply(compute_home_win_rate_adj, axis=1)
    df["away_win_rate_adj"] = df.apply(compute_away_win_rate_adj, axis=1)
    df["win_rate_diff"] = df["home_win_rate_adj"] - df["away_win_rate_adj"]
    return df

# ------------------ Main training script ------------------

def main():
    df = pd.read_csv("/Users/claudio/Documents/GitHub/ProgettoTesi/scripts/trainer/trainer_model.csv")

    df["game_duration"] = df["game_duration"].map(parse_duration)
    df = df[df["target_win"].notna()]
    df = add_advanced_features(df)

    num_cols = [
        "home_score_total", "away_score_total",
        "home_sets_won", "away_sets_won",
        "score_diff", "set_diff",
        "home_current_score", "away_current_score",
        "game_duration",
        "home_win_rate_last5", "away_win_rate_last5",
        "head_to_head_win_rate_home",
        "set_diff_current", "current_set_number", "set_importance",
        "home_win_rate_adj", "away_win_rate_adj", "win_rate_diff"
    ]
    cat_cols = ["home_team_id", "away_team_id"]

    X = df[num_cols + cat_cols].copy()
    y = df["target_win"].astype(int)

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
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

    clf.fit(X, y)

    joblib.dump(clf, "/Users/claudio/Documents/GitHub/ProgettoTesi/spark/models/model.joblib")
    print("✅ Modello addestrato e salvato in: model.joblib")

if __name__ == "__main__":
    main()
