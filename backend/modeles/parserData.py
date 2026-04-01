import json
from back.modeles.Agent import Agent

DEFAULT_MAX_TOKENS  = 1000
DEFAULT_TEMPERATURE = 0.3


def _creer_agent(node: dict) -> Agent:
    """Crée un Agent à partir d'un nœud JSON."""
    data = node["data"]
    return Agent(
        nom=node["id"],
        modele=data["model"],
        prompt=data["system_prompt"],
        max_token=data.get("max_tokens", DEFAULT_MAX_TOKENS),
        temperature=data.get("temperature", DEFAULT_TEMPERATURE),
    )


def parser(filepath: str):
    """
    Parse un fichier JSON de workflow et retourne le superviseur,
    la liste des agents spécialistes et le prompt utilisateur.

    Args:
        filepath (str): Chemin vers le fichier JSON du workflow.

    Returns:
        tuple: (superviseur, specialistes, prompt)

    Raises:
        ValueError: Si aucun superviseur n'est trouvé dans le JSON.

    Example:
        ```python
        superviseur, specialistes, prompt = parser("patern.json")
        orche = Orchestration(superviseur=superviseur, specialistes=specialistes)
        reponse = orche.executer(prompt)
        ```
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    superviseur  = None
    specialistes = []

    for node in data["nodes"]:
        if node["type"] == "supervisor":
            superviseur = _creer_agent(node)
        elif node["type"] == "agent":
            specialistes.append(_creer_agent(node))

    if superviseur is None:
        raise ValueError("Aucun nœud de type 'supervisor' trouvé dans le JSON.")

    prompt = data.get("input", {}).get("prompt", "")

    return superviseur, specialistes, prompt