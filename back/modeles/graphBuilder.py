import json
import re
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END


def extraire_json(texte: str) -> dict:
    """
    Extrait un objet JSON d'une réponse LLM même si elle contient
    du texte autour ou des blocs markdown (```json ... ```).
    """
    # Cas 1 : bloc markdown ```json ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", texte, re.DOTALL)
    if match:
        return json.loads(match.group(1))

    # Cas 2 : JSON brut quelque part dans le texte
    match = re.search(r"\{.*?\}", texte, re.DOTALL)
    if match:
        return json.loads(match.group(0))

    raise json.JSONDecodeError("Aucun JSON trouvé", texte, 0)


# --- 1. Définition de l'état ---
def update_results(current_results: dict, new_results: dict):
    """Permet d'accumuler les résultats des spécialistes sans les écraser."""
    if not current_results:
        return new_results
    updated = current_results.copy()
    updated.update(new_results)
    return updated


class OrchestrationState(TypedDict):
    user_input: str
    results: Annotated[dict, update_results]  # Dictionnaire accumulant les réponses { "nom_agent": "reponse" }
    next_agent: str  # Le nom du prochain agent à appeler, ou "reconstructeur"
    task_for_agent: str  # Le prompt spécifique généré par le superviseur pour ce spécialiste
    final_response: str  # La réponse finale pour l'utilisateur


# --- 2. Fonction de construction ---
def build_orchestration_graph(agent_superviseur, agents_specialistes: list, agent_reconstructeur):
    """
    Construit le graphe LangGraph.
    Hypothèse: tes agents ont un attribut 'nom' et une méthode 'executer_prompt'.
    """
    workflow = StateGraph(OrchestrationState)

    # --- Nœud du Superviseur ---
    def superviseur_node(state: OrchestrationState):
        noms_specialistes = [a.nom for a in agents_specialistes]
        resultats_actuels = state.get('results', {})
        print(f"\n[SUPERVISEUR] Analyse en cours... résultats déjà obtenus : {list(resultats_actuels.keys())}")

        prompt_sup = (
            f"Tâche initiale de l'utilisateur : {state['user_input']}\n"
            f"Résultats obtenus jusqu'à présent : {resultats_actuels}\n"
            f"Agents disponibles : {noms_specialistes}\n\n"
            "Analyse ce qui manque. Si tu as besoin d'un spécialiste, réponds STRICTEMENT avec un JSON : "
            '{"next_agent": "nom_du_specialiste", "prompt": "instructions_pour_lui"}. '
            "Si toutes les sous-tâches sont finies, réponds : "
            '{"next_agent": "reconstructeur", "prompt": ""}.'
        )

        response = agent_superviseur.executer_prompt(prompt_sup)
        print(f"[SUPERVISEUR] Décision brute : {response.content[:200]}")

        # Parse la réponse JSON du superviseur
        try:
            decision = extraire_json(response.content)
            print(f"[SUPERVISEUR] → Route vers : {decision['next_agent']}")
            return {
                "next_agent": decision["next_agent"],
                "task_for_agent": decision["prompt"]
            }
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[SUPERVISEUR] ⚠ Parsing JSON échoué ({e}) → fallback reconstructeur")
            return {"next_agent": "reconstructeur", "task_for_agent": ""}

    workflow.add_node("superviseur", superviseur_node)

    # --- Nœuds des Spécialistes ---
    # Fonction factory pour éviter le problème de late binding de Python dans les boucles
    def create_specialist_node(agent):
        def node(state: OrchestrationState):
            print(f"\n[{agent.nom.upper()}] Exécution en cours...")
            response = agent.executer_prompt(state["task_for_agent"])
            print(f"[{agent.nom.upper()}] Réponse reçue ({len(response.content)} caractères)")
            return {"results": {agent.nom: response.content}}

        return node

    for specialiste in agents_specialistes:
        workflow.add_node(specialiste.nom, create_specialist_node(specialiste))

    # --- Nœud du Reconstructeur ---
    def reconstructeur_node(state: OrchestrationState):
        print(f"\n[RECONSTRUCTEUR] Synthèse des résultats de : {list(state['results'].keys())}")
        prompt_rec = (
            f"Demande initiale : {state['user_input']}\n"
            f"Données brutes des spécialistes : {state['results']}\n\n"
            "Rédige la réponse finale complète et formatée pour l'utilisateur."
        )
        response = agent_reconstructeur.executer_prompt(prompt_rec)
        print(f"[RECONSTRUCTEUR] Réponse finale générée ({len(response.content)} caractères)")
        return {"final_response": response.content}

    workflow.add_node("reconstructeur", reconstructeur_node)

    # --- Configuration du Routing (Les Edges) ---
    workflow.set_entry_point("superviseur")

    # Fonction de routage conditionnel
    def route_from_supervisor(state: OrchestrationState):
        return state["next_agent"]

    # Le superviseur route vers un spécialiste ou le reconstructeur
    cibles_possibles = [a.nom for a in agents_specialistes] + ["reconstructeur"]
    workflow.add_conditional_edges(
        "superviseur",
        route_from_supervisor,
        {cible: cible for cible in cibles_possibles}  # Ex: {"agent_db": "agent_db", "reconstructeur": "reconstructeur"}
    )

    # Tous les spécialistes renvoient TOUJOURS au superviseur après leur tâche
    for specialiste in agents_specialistes:
        workflow.add_edge(specialiste.nom, "superviseur")

    # Le reconstructeur termine le graphe
    workflow.add_edge("reconstructeur", END)

    return workflow.compile()