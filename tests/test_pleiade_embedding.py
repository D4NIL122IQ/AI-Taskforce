import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN_PLEIADE")
BASE_URL = "https://pleiade.mi.parisdescartes.fr"

# ── Test 1 : voir les modèles disponibles ─────────────────────────────────────
print("=== Modèles disponibles sur Pléiade ===")
response = requests.get(
    f"{BASE_URL}/api/models",
    headers={"Authorization": f"Bearer {TOKEN}"}
)
print(f"Status : {response.status_code}")
if response.status_code == 200:
    modeles = response.json().get("data", [])
    for m in modeles:
        print(f"  - {m.get('id', m)}")
else:
    print(f"Erreur : {response.text}")

# ── Test 2 : tester l'endpoint embeddings ─────────────────────────────────────
print("\n=== Test endpoint embeddings ===")
response = requests.post(
    f"{BASE_URL}/api/embeddings",
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    },
    json={
        "model": "nomic-embed-text:latest",
        "input": "ceci est un test"
    }
)
print(f"Status : {response.status_code}")
if response.status_code == 200:
    data = response.json()
    vecteur = data["data"][0]["embedding"]
    print(f" Embeddings OK — dimension du vecteur : {len(vecteur)}")
    print(f"   Premiers éléments : {vecteur[:5]}")
else:
    print(f" Erreur : {response.text}")