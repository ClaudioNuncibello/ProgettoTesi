from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import urllib.request, json

app = FastAPI()

# abilitazione CORS per ogni origine (in dev va bene)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ES_BASE = "http://elasticsearch-volley:9200"
INDEX   = "volleyball_matches"

def es_search(payload: dict) -> dict:
    """Invia una POST a Elasticsearch e ritorna il JSON decodificato."""
    url = f"{ES_BASE}/{INDEX}/_search"
    body = json.dumps(payload).encode("utf-8")
    # usa POST così non ci sono dubbi sul body
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=502, detail=f"ES status {resp.status}")
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        # Passthrough degli errori 4xx/5xx di ES
        raise HTTPException(status_code=e.code, detail=e.reason)
    except Exception as e:
        # timeout, connessioni, JSON malformato...
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/match/{match_id}")
def get_match_data(match_id: int):
    # query esatta su intero
    query = {
        "query": {
            "term": {
                "match_id": match_id
            }
        },
        "sort": [
            {"timestamp": {"order": "desc"}}
        ],
        "size": 1
    }

    result = es_search(query)
    hits = result.get("hits", {}).get("hits", [])

    if not hits:
        raise HTTPException(status_code=404, detail="Match non trovato")

    # restituisci il documento più recente
    return hits[0]["_source"]
