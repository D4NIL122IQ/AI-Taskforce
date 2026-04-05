import requests
import json

# === Configuration ===
BASE_URL = "https://pleiade.mi.parisdescartes.fr"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImI2ZTdmNTFhLWQ3ZWEtNDZmNy05ZTBhLWE0YjQ4NjU3MTQ2NiIsImp0aSI6ImJmZDc5ZmZmLWUxYmItNGVlMy05NTMwLTljZTZjYjI5ZjQ5ZSJ9.NwRZc1PHjFJ79IlQ2aVlYjx9W0H1qG6MMrl0DNiY2tc"
MODEL = "athene-v2:latest"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def chat(message: str, conversation_history: list = None):
    """Envoie un message et récupère la réponse du LLM (format OpenAI-compatible)."""

    if conversation_history is None:
        conversation_history = []

    conversation_history.append({"role": "user", "content": message})

    payload = {
        "model": MODEL,
        "messages": conversation_history,
        "stream": True
    }

    response = requests.post(
        f"{BASE_URL}/api/chat/completions",
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

    print(f"Réponse : {full_response}")
    conversation_history.append({"role": "assistant", "content": full_response})

    return full_response, conversation_history


# === Utilisation ===
history = []

reponse, history = chat("donne moi la reponse a cette question combien fait 4+2*2   ", history)

