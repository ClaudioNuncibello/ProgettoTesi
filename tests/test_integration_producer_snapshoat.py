import sys
import os
import pytest
import pandas as pd
import json
from kafka import KafkaConsumer

# Path assoluto al tuo script
SCRIPT_DIR = "/Users/claudio/Documents/GitHub/ProgettoTesi/scripts"
sys.path.insert(0, SCRIPT_DIR)
import producerSnapshoat
from producerSnapshoat import create_producer, send_to_kafka, check_kafka_connection

# Questo è un test di integrazione singolo: rimuoviamo i marker personalizzati.

def test_send_and_consume_integration():
    # Controlla connessione a Kafka
    assert check_kafka_connection(), "Kafka non è raggiungibile"

    # Leggi dati dal CSV (nella stessa cartella di SCRIPT_DIR)
    csv_path = os.path.join(SCRIPT_DIR, '/Users/claudio/Documents/GitHub/ProgettoTesi/scripts/live_snapshots.csv')
    df = pd.read_csv(csv_path)
    rows = df.to_dict(orient='records')

    # Invia i dati reali a Kafka
    producer = create_producer()
    send_to_kafka(producer, rows)
    producer.flush()

    # Consuma i messaggi dal topic a partire dall'inizio
    consumer = KafkaConsumer(
        producerSnapshoat.TOPIC_NAME,
        bootstrap_servers='localhost:9092',
        auto_offset_reset='earliest',
        consumer_timeout_ms=10000
    )
    received = []
    for msg in consumer:
        received.append(json.loads(msg.value))
    consumer.close()

    # Verifica il conteggio dei messaggi
    assert len(received) == len(rows), \
        f"Messaggi ricevuti ({len(received)}) diverso dai record nel CSV ({len(rows)})"
