import requests
import json
import time

# Configurazione
API_KEY = "AymenURP9kWkgEatcBdcYA"
SEASON_ID = "47663"
KAFKA_BROKER = "localhost:9092"  # Broker Kafka in locale
TOPIC_NAME = "matchvolley"

# Endpoint API
url = f"https://volleyball.sportdevs.com/matches?season_id=eq.{SEASON_ID}"
headers = {
    'Accept': 'application/json',
    "Authorization": f"Bearer {API_KEY}"
}

def get_matches():
    """Recupera i dati grezzi dall'endpoint"""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Errore nel recupero dati: {str(e)}")
        return None



if __name__ == "__main__":
   
        print("Recupero dati dall'API SportDevs...")
        matches = get_matches()
        
        if matches:
            print(f"Trovate {len(matches)} partite")
            print(matches)
           