#!/usr/bin/env python3
"""
evaluate_model.py

Script per l'addestramento e valutazione offline di un modello predittivo (LogisticRegression)
basato su snapshot di partite di pallavolo. Il CSV contiene più istantanee per match_id e una colonna
target_win che indica il vincitore di ciascun match.
Il codice divide i dati a livello di match (per evitare leakage), allena il modello su un set di train,
e valuta su test tramite Accuracy, AUC-ROC, Log Loss e Brier Score.
"""

import re
import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, FunctionTransformer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import accuracy_score, roc_auc_score, log_loss, brier_score_loss
from sklearn.metrics import accuracy_score, roc_auc_score, log_loss, brier_score_loss

# ------------------ Funzioni di feature engineering ------------------

def parse_duration(s: str) -> float:
    if pd.isna(s) or s is None:
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
    if s.startswith("1") or "1st" in s:
        return 1
    if s.startswith("2") or "2nd" in s:
        return 2
    if s.startswith("3") or "3rd" in s:
        return 3
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
    df["current_set_number"] = df["match_status"].map(compute_current_set_number).astype(int)
    df["set_importance"] = df.apply(
        lambda row: compute_set_importance(
            row["home_sets_won"], row["away_sets_won"], row["current_set_number"]
        ), axis=1
    )
    df = compute_flags(df)
    df["home_win_rate_adj"] = df.apply(compute_home_win_rate_adj, axis=1)
    df["away_win_rate_adj"] = df.apply(compute_away_win_rate_adj, axis=1)
    df["win_rate_diff"] = df["home_win_rate_adj"] - df["away_win_rate_adj"]
    return df


def attenuate(X, alpha):
    return X * alpha


def main():
    # Carica dati
    df = pd.read_csv(
        "/Users/claudio/Documents/GitHub/ProgettoTesi/scripts/trainer/trainer_model.csv"
    )
    df["game_duration"] = df["game_duration"].map(parse_duration)
    df = df[df["target_win"].notna()]
    df = add_advanced_features(df)

    # Definizione features e gruppi
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
    groups = df["match_id"]

    # Split a livello di match_id
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(splitter.split(df, groups=groups))
    X_train = df.iloc[train_idx]
    X_test  = df.iloc[test_idx]
    y_train = X_train["target_win"].astype(int)
    y_test  = X_test["target_win"].astype(int)
    X_train = X_train[num_cols + cat_cols]
    X_test  = X_test [num_cols + cat_cols]

    # Preprocessing + attenuazione storiche
    alpha = 0.5
    hist_cols = ["home_win_rate_last5", "away_win_rate_last5", "head_to_head_win_rate_home"]
    other_num = [c for c in num_cols if c not in hist_cols]

    main_tf = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])
    hist_tf = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("attenuate", FunctionTransformer(func=attenuate, kw_args={"alpha": alpha}))
    ])
    cat_tf = OneHotEncoder(handle_unknown="ignore", sparse_output=False)

    preproc = ColumnTransformer(transformers=[
        ("num_main", main_tf, other_num),
        ("num_hist", hist_tf, hist_cols),
        ("cat", cat_tf, cat_cols)
    ], remainder="drop")

    pipe = Pipeline(steps=[
        ("preproc", preproc),
        ("lr", LogisticRegression(penalty="l2", C=1.0, max_iter=1000, random_state=42))
    ])

    # Training
    pipe.fit(X_train, y_train)

    # Predict e valutazione (soglia di classificazione = 0.5)
    y_proba = pipe.predict_proba(X_test)[:, 1]
    # Decisione binaria: 1 se proba >= 0.5, altrimenti 0
    y_pred = (y_proba >= 0.5).astype(int)
    print("# Soglia di classificazione usata per Accuracy: 0.5")
    print(f"Accuracy:    {accuracy_score(y_test, y_pred):.4f}")
    print(f"AUC-ROC:     {roc_auc_score(y_test, y_proba):.4f}")
    print(f"Log Loss:    {log_loss(y_test, y_proba):.4f}")
    print(f"Brier Score: {brier_score_loss(y_test, y_proba):.4f}")

if __name__ == "__main__":
    main()
