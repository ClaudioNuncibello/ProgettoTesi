from confluent_kafka import Producer
import json
import time
import random
import socket

def delivery_report(err, msg):
    """Callback per verificare l'esito dell'invio"""
    if err is not None:
        print(f"Messaggio fallito: {err}")
    else:
        print(f"Messaggio inviato a {msg.topic()} [{msg.partition()}]")

def main():
    # Configurazione del producer
    conf = {
        'bootstrap.servers': 'localhost:9092',  # Sostituisci con 'kafka-volley:9092' se esegui in Docker
        'client.id': socket.gethostname()
    }

    producer = Producer(conf)

    # Genera dati di esempio
    matches = [
        {
            "match_id": i,
            "team_a": "Team Alpha",
            "team_b": "Team Beta",
            "score_a": random.randint(10, 25),
            "score_b": random.randint(10, 25),
            "timestamp": int(time.time())
        }
        for i in range(1, 6)
    ]

    # Invio messaggi
    for match in matches:
        producer.produce(
            topic='matchvolley',
            value=json.dumps(match).encode('utf-8'),
            callback=delivery_report
        )
        print(f"Inviato: {match}")
    
    # Attesa completamento
    producer.flush()

if __name__ == "__main__":
    main()