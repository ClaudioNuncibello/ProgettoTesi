# 🏐 VolleyLive: Analisi Predittiva delle Partite di Pallavolo in Tempo Reale

## 🎯 Obiettivo del Progetto
VolleyLive è una piattaforma in tempo reale per il monitoraggio e l'analisi delle partite di pallavolo. Attraverso una pipeline dati always-on e un'interfaccia web interattiva, il sistema consente di raccogliere snapshot aggiornati di match live e calcolare una probabilità predittiva di vittoria per ciascuna squadra.

Il progetto unisce streaming Kafka, analisi Spark, indicizzazione su Elasticsearch e visualizzazione frontend in un ecosistema containerizzato e scalabile.

---

## ⚙️ Architettura Tecnologica

### 📦 Docker e Servizi
Tutti i servizi sono orchestrati tramite Docker Compose. I container attivi includono:

- **Kafka**: gestisce il topic `matchvolley` per lo streaming dei dati
- **Logstash**: trasforma e normalizza i dati prima dell'invio a Elasticsearch
- **Elasticsearch**: indicizza i documenti (snapshot) arricchiti con predizione
- **Kibana**: dashboard per ispezione e debug in tempo reale
- **Spark**: calcola il campo `predicted_win` utilizzando un modello di regressione logistic trained offline
- **Backend API (FastAPI)**: endpoint HTTP per recuperare i dati dei match da Elasticsearch
- **Frontend (React/Next.js)**: interfaccia moderna per seguire i match e visualizzare la probabilità predetta

---

## 🔁 Pipeline Dati

1. ▶️ **Producer Python**: esegue polling delle partite live dalle API SportDevs, filtra solo i match "seguiti" dall'utente e pubblica gli snapshot sul topic Kafka `matchvolley`
2. ▶️ **Spark Structured Streaming**:
   - legge gli snapshot da Kafka
   - estrae feature contestuali
   - applica un modello predittivo pre-addestrato
   - scrive il risultato su Elasticsearch
3. ▶️ **Elasticsearch**: indicizza i documenti con campi come punteggio, set, odds e `predicted_win`
4. ▶️ **Backend FastAPI**: fornisce un endpoint per recuperare uno snapshot tramite `match_id`
5. ▶️ **Frontend**: visualizza match, probabilità predetta e set live in tempo reale

---

## 📊 Predizione della Vittoria

Il campo `predicted_win` rappresenta la probabilità (tra 0 e 1) di vittoria per la squadra di casa, calcolata punto per punto. Il modello considera:

- differenziale di punteggio e set
- andamento del set corrente
- odds pre-partita
- storico dei match precedenti

La predizione viene aggiornata ogni 10 secondi e restituita insieme ai dati dello snapshot.

---

## 💻 Interfaccia Utente

- Costruita con **React + TailwindCSS**
- Utilizza l'API FastAPI per recuperare i dati Elasticsearch
- Visualizza:
  - Stato dei set live
  - Punteggio corrente
  - Gauge della probabilità di vittoria (Predicted Win)
  - Cronologia degli snapshot e andamento nel tempo

---

## 🧠 Machine Learning

Il modello è addestrato offline con dataset CSV contenente snapshot etichettati (`target_win`). Viene serializzato in formato MLlib e caricato in Spark Streaming.

**Algoritmo**: Logistic Regression con feature ingegnerizzate.

**Metriche raggiunte**:
- Accuracy: 74.62%
- AUC-ROC: 0.8479
- Brier Score: 0.1939

---

## 🔍 Debug e Osservabilità

- **Kibana** è preconfigurato per interrogare l'indice `volleyball_matches`
- **Kafka UI** permette di ispezionare i messaggi inviati nel topic
- **Logstash e Spark** scrivono log dettagliati nella console

---

## 📁 Struttura del Repository

```
.
├── docker-compose.yml          # File principale per il setup dei container
├── mapping.json                # File di mapping per l'indice di elastic
├── logstash/
│   └── logstash.conf           # Configurazione Logstash per la pipeline dati
├── spark/
│   └── spark.py                # Codice Spark per analisi predittive (WIP)
│   └── data/                   # Contiene live_snapshots_target.csv per il batch-training e pipeline model serializzato                
│       └── model/              # Contiene il modello di predizione
│   └── checkpoint/             # Contiene checkpoint per Elasticsearch streaming
├── frontend/                   # Web app React + Next.js
├── backtend/                   # Personal API di ricerca basata su Elasticsearch
├── producer/                   # Producer API
├── scripts/                    # Script Python per analisi
├── esdata/                     # Volume dati per Elasticsearch
└── README.md
```

---

## ✅ Stato del Progetto

| Componente                  | Stato           |
|-----------------------------|---------------- |
| Web App React               | ✅ Operativo     |
| Kafka                       | ✅ Operativo    |
| Logstash                    | ✅ Operativo    |
| Elasticsearch               | ✅ Operativo    |
| Kibana                      | ✅ Operativo    |
| Spark                       | ✅ Operativo    |
| Predizioni                  | ⚠️ Modello completato, miglioramento con raccolta dati  |
| Integrazione API SportDevs  | ✅ Completata   |

---

## 👨‍💻 Autore

Claudio Nuncibello  
[GitHub](https://github.com/ClaudioNuncibello)
