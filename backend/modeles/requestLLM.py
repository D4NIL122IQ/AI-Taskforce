import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://pleiade.mi.parisdescartes.fr/api/v1"
BASE_URL_NATIVE = "https://pleiade.mi.parisdescartes.fr/api"
MODEL = "phi4:latest"


def _get_headers() -> dict:
    """Lit le token à chaque appel pour prendre en compte les rafraîchissements."""
    token = os.environ.get("TOKEN_PLEIADE") or os.getenv("TOKEN_PLEIADE", "")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def chat(message: str, model: str, conversation_history: list = None, web_search: bool = False,
         temperature: float = None, max_tokens: int = None):
    """Envoie un message et récupère la réponse du LLM (format OpenAI-compatible)."""

    if conversation_history is None:
        conversation_history = []

    conversation_history.append({"role": "user", "content": message})

    payload = {
        "model": model,
        "messages": conversation_history,
        "stream": True
    }

    if temperature is not None:
        payload["temperature"] = temperature
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens

    if web_search:
        payload["features"] = {"web_search": True}
        payload["stream"] = True  # /api/chat/completions requiert stream=True
        url = f"{BASE_URL_NATIVE}/chat/completions"
    else:
        url = f"{BASE_URL}/chat/completions"

    response = requests.post(
        url,
        json=payload,
        headers=_get_headers(),
        stream=True,
        timeout=400
    )

    if response.status_code != 200:
        raise RuntimeError(f"Pléiade API error {response.status_code}: {response.text}")

    # Lire la réponse SSE (Server-Sent Events)
    full_response = ""
    for line in response.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            if decoded.startswith("data: "):
                decoded = decoded[6:]
            if decoded == "[DONE]":
                break
            try:
                data = json.loads(decoded)
                delta = data.get("choices", [{}])[0].get("delta", {})
                full_response += delta.get("content", "")
            except json.JSONDecodeError:
                pass

    conversation_history.append({"role": "assistant", "content": full_response})

    return full_response