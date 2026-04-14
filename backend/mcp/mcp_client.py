import re
import requests
from backend.mcp.connect_mcp import MCPConnection


class MCPCallError(Exception):
    pass


# ── Détection heuristique des outils nécessaires ─────────────────────────────

# Mots qui ne sont jamais des noms de dépôt (noms de services, quantificateurs…)
_FAUX_REPO_NOMS = {
    "github", "gitlab", "bitbucket", "git", "de", "du", "des", "mes",
    "les", "un", "une", "le", "la", "ce", "mon", "sur", "dans", "avec",
    "derniers", "dernières", "récents", "récentes", "publics", "privés",
    "tous", "toutes", "plusieurs", "quelques",
}

_REGLES_GITHUB = [
    # Listing de repos : "mes repos", "liste repos", "N derniers repos", "mes dépôts"
    (r"\b(list[e]?\s*(mes|les)?\s*(repos?|dépôts?|repositories)|mes\s+\d*\s*derniers?\s*(repos?|dépôts?)|derniers?\s+(repos?|dépôts?))\b",
     "list_repos", lambda m, msg: {}),

    # Issues sur un repo précis
    (r"\b(issues?|problèmes?|tickets?)\s+d[eu]\s+(\w[\w\-\.]+)\b",
     "list_issues", lambda m, msg: {"repo": m.group(2)}),
    # Issues en général
    (r"\b(issues?|problèmes?|tickets?)\b",
     "list_issues", lambda m, msg: {}),

    # Commits sur un repo précis
    (r"\b(commits?|historique)\s+d[eu]\s+(\w[\w\-\.]+)\b",
     "list_commits", lambda m, msg: {"repo": m.group(2)}),

    # get_repo : seulement si le mot après "repo/dépôt" est un vrai nom (pas dans la denylist)
    (r"\b(?:le\s+repo|du\s+repo|mon\s+repo|dépôt|repository)\s+(\w[\w\-\.]+)\b",
     "get_repo", lambda m, msg: {"repo": m.group(1)} if m.group(1).lower() not in _FAUX_REPO_NOMS else None),

    # Recherche de code
    (r"\b(cherch[e]?|search|trouve)\s+(.+?)\s+(dans|in|sur)\s+(mes)?\s*(repos?|dépôts?|code)\b",
     "search_code", lambda m, msg: {"query": m.group(2)}),

    # Pull requests sur un repo précis
    (r"\b(pull\s*requests?|PR)\s+d[eu]\s+(\w[\w\-\.]+)\b",
     "get_pull_request", lambda m, msg: {"repo": m.group(2)}),
]

_REGLES_GMAIL = [
    (r"\b(list[e]?\s*(mes)?\s*(mails?|emails?|messages?))\b", "list_messages", lambda m, msg: {}),
    (r"\b(cherch[e]?|search|trouve)\s+(.+?)\s+(dans|in)\s+(mes)?\s*(mails?|emails?)\b", "search_messages", lambda m, msg: {"query": m.group(2)}),
    (r"\b(envoie?|send)\s+.+\b", "send_message", lambda m, msg: {}),
    (r"\b(labels?|catégories?)\b", "list_labels", lambda m, msg: {}),
]


def detecter_outils_necessaires(message: str, capabilities: list) -> list:
    """
    Détecte les outils MCP à appeler en analysant le message par mots-clés.

    Args:
        message (str): Message de l'utilisateur.
        capabilities (list): Capacités disponibles sur la connexion MCP.

    Returns:
        list[tuple[str, dict]]: Liste de (nom_outil, params) à exécuter.
    """
    msg_lower = message.lower()
    outils_trouves = []
    outils_vus = set()

    # Détecter si on parle de GitHub ou Gmail selon les capabilities
    regles = []
    if any(c in capabilities for c in ["list_repos", "list_issues", "search_code"]):
        regles = _REGLES_GITHUB
    elif any(c in capabilities for c in ["list_messages", "send_message"]):
        regles = _REGLES_GMAIL

    for pattern, outil, extraire_params in regles:
        if outil not in capabilities:
            continue
        if outil in outils_vus:
            continue
        match = re.search(pattern, msg_lower)
        if match:
            try:
                params = extraire_params(match, msg_lower)
            except Exception:
                params = {}
            if params is None:   # extracteur a explicitement rejeté le match
                continue
            outils_trouves.append((outil, params))
            outils_vus.add(outil)

    # Fallback : si rien détecté mais le message parle de GitHub en général
    if not outils_trouves and any(c in capabilities for c in ["list_repos"]):
        if any(mot in msg_lower for mot in ["github", "repo", "dépôt", "code", "projet"]):
            outils_trouves.append(("list_repos", {}))

    return outils_trouves


# ── Appels HTTP réels ────────────────────────────────────────────────────────

def appeler_outil_mcp(connection: MCPConnection, outil: str, params: dict, timeout: int = 15) -> dict:
    """
    Dispatch l'appel vers le bon client selon l'URL de la connexion.

    Args:
        connection (MCPConnection): Connexion MCP active.
        outil (str): Nom de l'outil à appeler.
        params (dict): Paramètres de l'outil.
        timeout (int): Timeout HTTP en secondes.

    Returns:
        dict: Résultat brut de l'API.

    Raises:
        MCPCallError: Si l'appel échoue.
    """
    if "githubcopilot.com" in connection.url:
        return _appel_jsonrpc(connection, outil, params, timeout)
    elif connection.mcp == "github":
        return _appel_rest_github(connection, outil, params, timeout)
    elif connection.mcp == "gmail":
        return _appel_rest_gmail(connection, outil, params, timeout)
    else:
        raise MCPCallError(f"MCP '{connection.mcp}' non supporté dans mcp_client")


def _appel_rest_github(connection: MCPConnection, outil: str, params: dict, timeout: int) -> dict:
    """Appelle l'API REST GitHub avec un PAT classique."""
    BASE = "https://api.github.com"
    headers = {**connection.headers, "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    # Retirer les headers internes non reconnus par GitHub
    headers.pop("X-Public-Token", None)

    owner = params.get("owner", "")
    repo = params.get("repo", "")

    if outil == "list_repos":
        url = f"{BASE}/user/repos?per_page=50&sort=updated"
        resp = requests.get(url, headers=headers, timeout=timeout)

    elif outil == "list_issues":
        if owner and repo:
            url = f"{BASE}/repos/{owner}/{repo}/issues?per_page=20&state=open"
        elif repo:
            # Tenter sans owner — récupère d'abord l'utilisateur
            user = _get_github_user(headers, timeout)
            url = f"{BASE}/repos/{user}/{repo}/issues?per_page=20&state=open"
        else:
            url = f"{BASE}/issues?per_page=20&filter=assigned&state=open"
        resp = requests.get(url, headers=headers, timeout=timeout)

    elif outil == "get_repo":
        if not repo:
            raise MCPCallError("get_repo nécessite un paramètre 'repo'")
        if not owner:
            owner = _get_github_user(headers, timeout)
        url = f"{BASE}/repos/{owner}/{repo}"
        resp = requests.get(url, headers=headers, timeout=timeout)

    elif outil == "create_issue":
        if not repo:
            raise MCPCallError("create_issue nécessite un paramètre 'repo'")
        if not owner:
            owner = _get_github_user(headers, timeout)
        url = f"{BASE}/repos/{owner}/{repo}/issues"
        payload = {"title": params.get("title", "Nouvelle issue"), "body": params.get("body", "")}
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)

    elif outil == "search_code":
        query = params.get("query", "")
        if not query:
            raise MCPCallError("search_code nécessite un paramètre 'query'")
        url = f"{BASE}/search/code?q={requests.utils.quote(query)}&per_page=10"
        resp = requests.get(url, headers=headers, timeout=timeout)

    elif outil == "list_commits":
        if not repo:
            raise MCPCallError("list_commits nécessite un paramètre 'repo'")
        if not owner:
            owner = _get_github_user(headers, timeout)
        url = f"{BASE}/repos/{owner}/{repo}/commits?per_page=10"
        resp = requests.get(url, headers=headers, timeout=timeout)

    elif outil == "get_pull_request":
        if not repo:
            raise MCPCallError("get_pull_request nécessite un paramètre 'repo'")
        if not owner:
            owner = _get_github_user(headers, timeout)
        pull_number = params.get("pull_number", "")
        if pull_number:
            url = f"{BASE}/repos/{owner}/{repo}/pulls/{pull_number}"
        else:
            url = f"{BASE}/repos/{owner}/{repo}/pulls?per_page=10&state=open"
        resp = requests.get(url, headers=headers, timeout=timeout)

    else:
        raise MCPCallError(f"Outil GitHub inconnu : {outil}")

    if resp.status_code not in (200, 201):
        raise MCPCallError(f"GitHub API {resp.status_code} sur '{outil}': {resp.text[:200]}")

    return resp.json()


def _get_github_user(headers: dict, timeout: int) -> str:
    """Récupère le login GitHub de l'utilisateur authentifié."""
    resp = requests.get("https://api.github.com/user", headers=headers, timeout=timeout)
    if resp.status_code == 200:
        return resp.json().get("login", "")
    return ""


def _appel_rest_gmail(connection: MCPConnection, outil: str, params: dict, timeout: int) -> dict:
    """Appelle l'API REST Gmail."""
    BASE = "https://gmail.googleapis.com/gmail/v1/users/me"
    headers = {**connection.headers}
    headers.pop("X-Public-Token", None)

    if outil == "list_messages":
        url = f"{BASE}/messages?maxResults=10"
        resp = requests.get(url, headers=headers, timeout=timeout)

    elif outil == "search_messages":
        query = params.get("query", "")
        url = f"{BASE}/messages?q={requests.utils.quote(query)}&maxResults=10"
        resp = requests.get(url, headers=headers, timeout=timeout)

    elif outil == "list_labels":
        url = f"{BASE}/labels"
        resp = requests.get(url, headers=headers, timeout=timeout)

    elif outil == "get_message":
        msg_id = params.get("id", "")
        if not msg_id:
            raise MCPCallError("get_message nécessite un paramètre 'id'")
        url = f"{BASE}/messages/{msg_id}?format=full"
        resp = requests.get(url, headers=headers, timeout=timeout)

    else:
        raise MCPCallError(f"Outil Gmail non supporté en pré-fetch : {outil}")

    if resp.status_code != 200:
        raise MCPCallError(f"Gmail API {resp.status_code} sur '{outil}': {resp.text[:200]}")

    return resp.json()


def _appel_jsonrpc(connection: MCPConnection, outil: str, params: dict, timeout: int) -> dict:
    """Appel JSON-RPC 2.0 vers le serveur MCP GitHub Copilot."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": outil,
            "arguments": params,
        },
    }
    resp = requests.post(connection.url, json=payload, headers=connection.headers, timeout=timeout)
    if resp.status_code != 200:
        raise MCPCallError(f"MCP JSON-RPC {resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    if "error" in data:
        raise MCPCallError(f"MCP JSON-RPC error: {data['error']}")

    return data.get("result", {})


# ── Formattage des résultats ─────────────────────────────────────────────────

def formater_resultats_mcp(resultats: list, mcp_name: str) -> str:
    """
    Formate les résultats bruts des appels MCP en bloc texte pour le prompt.

    Args:
        resultats (list[tuple[str, dict]]): Liste de (nom_outil, données).
        mcp_name (str): Nom affiché du service MCP.

    Returns:
        str: Bloc texte prêt à être injecté dans le system prompt.
    """
    blocs = []

    for outil, data in resultats:
        lignes = [f"[Données {mcp_name} — {outil}]"]

        if outil == "list_repos" and isinstance(data, list):
            for repo in data[:20]:
                lang = repo.get("language") or "?"
                visibilite = "privé" if repo.get("private") else "public"
                stars = repo.get("stargazers_count", 0)
                lignes.append(f"• {repo['full_name']} ({visibilite}) — {lang} — {stars} stars")

        elif outil == "list_issues" and isinstance(data, list):
            for issue in data[:15]:
                lignes.append(f"• #{issue.get('number')} {issue.get('title')} [{issue.get('state')}]")

        elif outil == "get_repo" and isinstance(data, dict):
            lignes.append(f"• Nom : {data.get('full_name')}")
            lignes.append(f"• Langage : {data.get('language') or '?'}")
            lignes.append(f"• Description : {data.get('description') or 'aucune'}")
            lignes.append(f"• Stars : {data.get('stargazers_count', 0)}")
            lignes.append(f"• Visibilité : {'privé' if data.get('private') else 'public'}")

        elif outil == "search_code" and isinstance(data, dict):
            items = data.get("items", [])
            for item in items[:10]:
                lignes.append(f"• {item.get('repository', {}).get('full_name', '?')} — {item.get('path', '?')}")

        elif outil == "list_commits" and isinstance(data, list):
            for commit in data[:10]:
                msg = commit.get("commit", {}).get("message", "").split("\n")[0]
                author = commit.get("commit", {}).get("author", {}).get("name", "?")
                lignes.append(f"• {author} : {msg}")

        elif outil == "list_messages" and isinstance(data, dict):
            messages = data.get("messages", [])
            lignes.append(f"• {len(messages)} message(s) trouvé(s)")

        elif outil == "list_labels" and isinstance(data, dict):
            for label in data.get("labels", [])[:15]:
                lignes.append(f"• {label.get('name')}")

        else:
            # Fallback générique
            lignes.append(str(data)[:500])

        blocs.append("\n".join(lignes))

    return "\n\n".join(blocs)
