import json
import os
from dataclasses import dataclass

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "mcp_config.json")
SUPPORTED_MCPS = {"github", "gmail"}


@dataclass
class MCPConnection:
    mcp: str
    name: str
    transport: str
    url: str
    headers: dict
    scopes: list
    capabilities: list


def connect_mcp(token_public: str, token_tempo: str, mcp: str) -> MCPConnection:
    """
    Construit la connexion à un MCP donné à partir des tokens fournis.

    Les tokens seront récupérés depuis la base de données par l'appelant ;
    cette fonction se contente de construire et retourner la configuration
    de connexion prête à l'emploi.

    Args:
        token_public (str): Token public / client ID de l'utilisateur.
        token_tempo  (str): Token temporaire / access token (Bearer ou OAuth2).
        mcp          (str): Identifiant du MCP cible — "github" ou "gmail".

    Returns:
        MCPConnection: Objet contenant toutes les informations nécessaires
                       pour initialiser un client MCP (url, headers, scopes…).

    Raises:
        ValueError: Si le MCP demandé n'est pas supporté.
        FileNotFoundError: Si le fichier de configuration est introuvable.


    """
    if mcp not in SUPPORTED_MCPS:
        raise ValueError(
            f"MCP '{mcp}' non supporté. Valeurs acceptées : {sorted(SUPPORTED_MCPS)}"
        )

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    mcp_cfg = config[mcp]
    auth_cfg = mcp_cfg["auth"]

    headers = {
        auth_cfg["header"]: f"{auth_cfg['prefix']} {token_tempo}",
        "X-Public-Token": token_public,
        "Content-Type": "application/json",
    }

    return MCPConnection(
        mcp=mcp,
        name=mcp_cfg["name"],
        transport=mcp_cfg["transport"],
        url=mcp_cfg["url"],
        headers=headers,
        scopes=mcp_cfg["scopes"],
        capabilities=mcp_cfg["capabilities"],
    )