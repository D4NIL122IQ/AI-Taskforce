import requests
from backend.modeles.requestLLM import embed  # <-- importe embed, pas chat

# 1. Auth
auth = requests.post(
    "https://pleiade.mi.parisdescartes.fr/api/v1/auths/signin",
    json={
        "email": "laye-fode.keita@etu.u-paris.fr",
        "password": "ciBtiz-qevtih-5pozxu"
    }
)
data = auth.json()
import os
os.environ["TOKEN_PLEIADE"] = data.get("access_token") or data.get("token", "")
print(f"Token obtenu : {data.get('token', '')}")  # Affiche les 10 premiers caractères du token

# 2. Test embedding
vector = embed("Bonjour, comment ça va ?")
print("Dimension:", len(vector))