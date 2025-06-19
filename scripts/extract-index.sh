#!/usr/bin/env bash
set -euo pipefail

HOST="localhost:9200"
INDEX="volleyball_matches"
SIZE=500          # batch size
SCROLL="2m"       # durata dello scroll
OUT="volleyball_dump.jsonl"

echo "▶︎ Primo batch..."
resp=$(curl -s -H 'Content-Type: application/json' \
            -X POST "$HOST/$INDEX/_search?scroll=$SCROLL&size=$SIZE" \
            -d '{"query":{"match_all":{}}}')

# estraggo _scroll_id e i documenti
scroll_id=$(echo "$resp" | jq -r '._scroll_id')
echo "$resp" | jq -c '.hits.hits[]._source' > "$OUT"

while : ; do
  echo "▶︎ Batch successivo..."
  resp=$(curl -s -H 'Content-Type: application/json' \
              -X POST "$HOST/_search/scroll" \
              -d "{\"scroll\":\"$SCROLL\",\"scroll_id\":\"$scroll_id\"}")

  # se non ci sono più risultati esco
  hits=$(echo "$resp" | jq '.hits.hits | length')
  [[ "$hits" -eq 0 ]] && break

  # appendo i nuovi documenti
  echo "$resp" | jq -c '.hits.hits[]._source' >> "$OUT"
  scroll_id=$(echo "$resp" | jq -r '._scroll_id')
done

echo "✅ Esportazione terminata: $OUT"
