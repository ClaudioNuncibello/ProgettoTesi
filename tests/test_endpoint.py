#!/usr/bin/env python3
import requests, json

API_KEY = "AymenURP9kWkgEatcBdcYA"
BASE = "https://volleyball.sportdevs.com/matches"

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def prova(url):
    print(f"\n🔗 URL: {url}")
    try:
        r = requests.get(url, headers= headers, timeout=10)
        print(f"→ Status: {r.status_code}")
        if r.ok:
            print("→ JSON ricevuto:")
            print(json.dumps(r.json()))
        else:
            print("→ Corpo risposta (snippet):")
            print(r.text[:200], "…")
    except Exception as e:
        print(f"❌ Errore richiesta: {e}")

def main():
    prova(f"{BASE}?season_id=eq.17700&limit=5")
if __name__ == "__main__":
    main()
