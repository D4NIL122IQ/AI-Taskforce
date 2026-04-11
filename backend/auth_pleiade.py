import os
import re
import requests
from pathlib import Path
from dotenv import load_dotenv

SIGNIN_URL = "https://pleiade.mi.parisdescartes.fr/api/v1/auths/signin"
ENV_PATH   = Path(__file__).resolve().parents[1] / ".env"


def refresh_token() -> str | None:
    """
    S'authentifie sur Pléiade avec PLEIADE_EMAIL / PLEIADE_PASSWORD,
    met à jour TOKEN_PLEIADE dans le fichier .env et dans os.environ.
    Retourne le nouveau token, ou None si échec.
    """
    load_dotenv(ENV_PATH, override=True)

    email    = os.getenv("PLEIADE_EMAIL", "").strip()
    password = os.getenv("PLEIADE_PASSWORD", "").strip()

    if not email or not password:
        print("[Pléiade] PLEIADE_EMAIL ou PLEIADE_PASSWORD non définis dans .env — token non rafraîchi.")
        return None

    try:
        resp = requests.post(
            SIGNIN_URL,
            json={"email": email, "password": password},
            timeout=15,
        )
        resp.raise_for_status()
        token = resp.json().get("token")
        if not token:
            print(f"[Pléiade] Réponse inattendue : {resp.json()}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"[Pléiade] Échec de l'authentification : {e}")
        return None

    # Mise à jour dans os.environ (utilisé par requestLLM.py dès maintenant)
    os.environ["TOKEN_PLEIADE"] = token

    # Mise à jour persistante dans le fichier .env
    env_text = ENV_PATH.read_text(encoding="utf-8")
    new_line  = f'TOKEN_PLEIADE = "{token}"'
    if re.search(r"^TOKEN_PLEIADE\s*=", env_text, re.MULTILINE):
        env_text = re.sub(r"^TOKEN_PLEIADE\s*=.*$", new_line, env_text, flags=re.MULTILINE)
    else:
        env_text = new_line + "\n" + env_text
    ENV_PATH.write_text(env_text, encoding="utf-8")

    print("[Pléiade] Token rafraîchi avec succès.")
    return token
