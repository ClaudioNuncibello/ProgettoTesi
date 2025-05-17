🏐 VolleyLive: Piattaforma di Monitoraggio e Analisi delle Partite di Pallavolo in Tempo Reale
🎯 Obiettivo del Progetto
VolleyLive è un sistema completo per il monitoraggio in tempo reale delle partite di pallavolo, con l’obiettivo di raccogliere, visualizzare e successivamente analizzare i dati live tramite predizioni basate su snapshot temporali. Il progetto unisce una pipeline dati moderna con una web app interattiva, permettendo agli utenti di selezionare i match preferiti e attivare una catena di elaborazione che include strumenti come Kafka, Logstash, Elasticsearch e Kibana.

⚙️ Architettura Tecnologica
📦 1. Docker e Containerizzazione
L'intero sistema è containerizzato tramite Docker Compose, con una rete isolata in cui comunicano i seguenti servizi:

Zookeeper e Kafka per la gestione dei flussi di dati (event streaming).

Kafka-UI per il monitoraggio dei topic.

Logstash per trasformare e inoltrare i dati.

Elasticsearch per l'indicizzazione e lo storage strutturato.

Kibana per la visualizzazione grafica dei dati in tempo reale.

Spark è predisposto per futuri sviluppi di Machine Learning sui dati snapshot, ma attualmente non è ancora operativo.

🔁 2. Pipeline Dati
I dati delle partite live (come punteggi, set, stato partita) vengono prelevati via API e pubblicati su Kafka nel topic matchvolley.

Logstash legge da Kafka, esegue trasformazioni (es. mapping dei punteggi, format JSON) e inoltra i dati a Elasticsearch.

Kibana permette di visualizzare i dati in tempo reale in dashboard personalizzate.

I dati raccolti costituiscono anche le snapshot utilizzate per future predizioni tramite Spark.

🌐 3. Interfaccia Web (Frontend + Backend)
La parte frontend è un’app moderna costruita con:

React + Next.js (App Router)

TypeScript per sicurezza e robustezza

TailwindCSS per uno styling reattivo e modulare

Node.js come runtime backend

pnpm per una gestione efficiente delle dipendenze

Docker (Node 18) per il deployment

Funzionalità principali della web app:

Visualizzazione delle partite in diretta con aggiornamenti in tempo reale

Possibilità di “seguire” (stellina) un match: questo attiva la pipeline di streaming dati per quella specifica partita

Statistiche e stato del match aggiornati ogni 10 secondi

Predizioni future basate sui dati raccolti per ciascuna partita

📊 Predizioni e Analisi (Prossimi Sviluppi)
Il modulo Spark, già containerizzato, sarà utilizzato per analizzare le snapshot raccolte. Le snapshot sono strutture dati che rappresentano lo stato completo del match a intervalli regolari (es. ogni 10 secondi). Da queste verranno estratte feature per:

Calcolare la probabilità di vittoria in tempo reale (WinScore)

Analizzare i trend di squadra

Migliorare l’esperienza dell’utente fornendo insight predittivi

🧩 Vantaggi del Sistema
Completamente containerizzato e scalabile

Progettato per flussi di dati real-time e big data

Interfaccia utente moderna e reattiva

Predisposizione per moduli avanzati di Machine Learning

Dashboard visiva accessibile via Kibana

✅ Stato Attuale
Web app funzionante con selezione partite preferite

Pipeline Kafka → Logstash → Elasticsearch → Kibana attiva

Spark integrato ma in attesa di dati snapshot e modelli predittivi

Dataset live verificato tramite chiamate API

Docker Compose stabile e pronto per ambienti ARM64
