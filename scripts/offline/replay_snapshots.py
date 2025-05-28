#!/usr/bin/env python3
import pandas as pd
from kafka import KafkaProducer
import json

# — Configurazione —
CSV_PATH = "/Users/claudio/Documents/GitHub/ProgettoTesi/scripts/live_snapshots.csv"
KAFKA_BROKER = "localhost:9092"
TOPIC_NAME   = "matchvolley"

# Producer Kafka (serializza anche datetime)
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
    acks=1
)

# Leggo il CSV; parsing automatico di timestamp come datetime
df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])

print(f"🔁 Invio {len(df)} record da {CSV_PATH} a Kafka…")

for _, row in df.iterrows():
    # Converto la riga in dizionario; assicuro timestamp ISO8601
    record = row.to_dict()
    #record["timestamp"] = row["timestamp"].isoformat()
    record["timestamp"] = row["timestamp"].isoformat(sep=" ")
    
    # Invio
    producer.send(TOPIC_NAME, value=record).add_callback(
        lambda md: print(f"✅ Sent match_id={record['match_id']} partition={md.partition}")
    ).add_errback(
        lambda err: print(f"❌ Error sending match_id={record['match_id']}: {err}")
    )

# Forzo il flush e chiudo
producer.flush()
producer.close()

print("🏁 Tutti i record inviati.")
