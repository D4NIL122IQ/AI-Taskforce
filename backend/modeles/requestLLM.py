import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://pleiade.mi.parisdescartes.fr/api/v1"
TOKEN = os.getenv("TOKEN_PLEIADE")
MODEL = "athene-v2:latest"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def chat(message: str, model: str, conversation_history: list = None):
    """Envoie un message et récupère la réponse du LLM (format OpenAI-compatible)."""

    if conversation_history is None:
        conversation_history = []

    conversation_history.append({"role": "user", "content": message})

    payload = {
        "model": model,
        "messages": conversation_history,
        "stream": True
    }

    response = requests.post(
        f"{BASE_URL}/chat/completions",
        json=payload,
        headers=headers,
        stream=True
    )

    if response.status_code != 200:
        print(f"Erreur {response.status_code}: {response.text}")
        return None, conversation_history

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