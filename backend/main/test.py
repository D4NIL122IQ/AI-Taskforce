import requests
from backend.modeles.Agent import Agent

# 1. Authentification
auth = requests.post(
    "https://pleiade.mi.parisdescartes.fr/api/v1/auths/signin",
    json={
        "email":"laye-fode.keita@etu.u-paris.fr",
        "password": ""
    }
)

data = auth.json()
TOKEN_CACHE = data.get("access_token") or data.get("token")

print(TOKEN_CACHE)