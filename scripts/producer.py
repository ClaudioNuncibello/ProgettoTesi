import requests
from kafka import KafkaProducer
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

def create_producer():
    """Crea un producer Kafka una sola volta"""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks=1
    )

def success(metadata):
    print(f"Messaggio inviato con successo a {metadata.topic} [partizione {metadata.partition}]")

def failure(exception):
    print(f"Errore nell'invio a Kafka: {exception}")

def send_to_kafka(producer, matches):
    """Invia i dati a Kafka con un producer riutilizzabile"""
    for match in matches:
        producer.send(TOPIC_NAME, match).add_callback(success).add_errback(failure)
    producer.flush()

def check_kafka_connection():
    """Verifica se Kafka è attivo prima di inviare dati"""
    try:
        producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)
        producer.close()
        return True
    except Exception as e:
        print(f"Kafka non è raggiungibile: {str(e)}")
        return False

if __name__ == "__main__":
    print("Verifica connessione a Kafka...")
    if check_kafka_connection():
        producer = create_producer()
        print("Recupero dati dall'API SportDevs...")
        matches = get_matches()
        
        if matches:
            print(f"Trovate {len(matches)} partite")
            send_to_kafka(producer, matches)
            print("Dati inviati con successo a Kafka")
        else:
            print("Nessun dato recuperato dall'API")
        
        producer.close()
    else:
        print("Errore: Kafka non è disponibile.")
