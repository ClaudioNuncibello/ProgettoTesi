import requests

API_KEY = "AymenURP9kWkgEatcBdcYA"
BASE_URL = "https://volleyball.sportdevs.com"
HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def get_live_matches():
    """Recupera l’elenco delle partite live."""
    url = f"{BASE_URL}/matches?status_type=eq.live"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

def get_live_coverage(match_id):
    """
    Restituisce un dict con booleane per ogni mercato
    (es. match_winner, sets_points_handicap, etc.)
    """
    url = f"{BASE_URL}/odds/coverage-live?match_id=eq.{match_id}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    return data[0] if data else {}

def get_odds_for_market(match_id, market):
    """
    Richiama l’endpoint odds/{market} con is_live=true
    e restituisce il JSON.
    """
    url = f"{BASE_URL}/odds/{market}?match_id=eq.{match_id}&is_live=eq.true"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

def main():
    matches = get_live_matches()
    if not matches:
        print("Nessuna partita live in corso.")
        return

    for match in matches:
        match_id = match["id"]
        print(f"\n🏐 Partita Live ID={match_id}:")
        coverage = get_live_coverage(match_id)
        # Coverage Live endpoint :contentReference[oaicite:0]{index=0}
        for market, enabled in coverage.items():
            if market == "match_id" or not enabled:
                continue
            print(f" • Mercato '{market}' attivo, recupero quote…")
            # map di nomi mercato → path endpoint
            # gli endpoint usano trattini minuscoli:
            market_path = market.replace("_", "-")
            odds = get_odds_for_market(match_id, market_path)
            print(f"   → {market} odds:", odds)

if __name__ == "__main__":
    main()
