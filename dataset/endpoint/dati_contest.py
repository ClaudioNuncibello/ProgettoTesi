import requests
import pandas as pd

API_KEY = "AymenURP9kWkgEatcBdcYA"
SEASON_ID = "47663"
KAFKA_BROKER = "localhost:9092"
TOPIC_NAME = "matchvolley"

headers = {
    'Accept': 'application/json',
    "Authorization": f"Bearer {API_KEY}"
}

def get_matches_for_team(team_id):
    """Recupera i match di una squadra (casa o trasferta)"""
    url = f"https://volleyball.sportdevs.com/matches?or=(home_team_id.eq.{team_id},away_team_id.eq.{team_id})&order=specific_start_time.desc&limit=15"
    response = requests.get(url, headers=headers)
    return response.json()


def build_match_dataframe(matches, team_type):
    data = []
    for match in matches:
        home_score = match.get("home_team_score", {}).get("display", None)
        away_score = match.get("away_team_score", {}).get("display", None)
        
        data.append({
            'match_id': match.get("id", ""),
            'match_name': match.get("name", ""),
            'score': f"{home_score} - {away_score}" if home_score is not None and away_score is not None else None
        })
    
    return pd.DataFrame(data)

# Eseguiamo la funzione per ottenere gli incontri per due squadre
home_team_id = 1883
away_team_id = 1847

home_matches = get_matches_for_team(home_team_id)
away_matches = get_matches_for_team(away_team_id)

df_home_matches = build_match_dataframe(home_matches, "home")
df_away_matches = build_match_dataframe(away_matches, "away")

# Crea un DataFrame con solo i testa a testa
common_match_ids = set(df_home_matches["match_id"]) & set(df_away_matches["match_id"])
df_head_to_head = pd.concat([df_home_matches, df_away_matches])
df_head_to_head = df_head_to_head[df_head_to_head["match_id"].isin(common_match_ids)]

# Rimuove eventuali duplicati
df_head_to_head = df_head_to_head.drop_duplicates(subset="match_id").sort_values(by="match_id", ascending=False).head(15)

# Mostra i due DataFrame
print("Home team matches:")
print(df_home_matches)

print("\nAway team matches:")
print(df_away_matches)

print("\nhead to head matches:")
print(df_head_to_head)
