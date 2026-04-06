import os
from ddgs import DDGS
from langchain_community.tools.tavily_search import TavilySearchResults


def format_results(results):
    """Formate les résultats de recherche en texte propre (titre, contenu, url)."""
    formatted = []

    for r in results:
        title = r.get("title", "")
        content = r.get("content") or r.get("body", "")
        url = r.get("url") or r.get("href", "")

        content = content.replace("\n", " ").strip()
        formatted.append(f"{title}\n{content}\n{url}")

    return "\n\n".join(formatted)


def search_ddg(query: str, max_results: int = 3) -> str:
    """Recherche via DuckDuckGo et retourne un texte formaté."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return "Aucun résultat trouvé"

        return format_results(results)

    except Exception as e:
        return f"Erreur DDG: {str(e)}"


def search_tavily(query: str, max_results: int = 5) -> str:
    """Recherche via Tavily (clé API requise) et retourne un texte formaté."""
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "Clé Tavily manquante"

        search = TavilySearchResults(
            tavily_api_key=api_key,
            max_results=max_results
        )

        return format_results(search.invoke(query))

    except Exception as e:
        return f"Erreur Tavily: {str(e)}"


def search_web(query: str, provider: str = "ddg") -> str:
    """Point d’entrée : choisit le moteur (tavily ou ddg) avec fallback."""
    if provider == "tavily":
        result = search_tavily(query)
        return search_ddg(query) if "Erreur" in result or "manquante" in result else result

    elif provider == "ddg":
        return search_ddg(query)

    return "Provider inconnu"