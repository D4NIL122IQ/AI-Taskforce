import json
import re
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.constants import Send
from backend.services.docx_generator_service import generer_docx


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
    match = re.search(r"\{.*?\}"
                      , texte, re.DOTALL)
    if match:
        return json.loads(match.group(0))

    raise json.JSONDecodeError("Aucun JSON trouvé", texte, 0)

def extraire_json_souple(texte: str) -> dict:
    match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", texte, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", texte, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return extraire_json(texte)


# --- 1. Définition de l'état ---
def update_results(current_results: dict, new_results: dict):
    """Permet d'accumuler les résultats des spécialistes sans les écraser."""
    if not current_results:
        return new_results
    updated = current_results.copy()
    updated.update(new_results)
    return updated

# Ajouter cette fonction avant OrchestrationState
def update_logs(current_logs: list, new_logs: list):
    if not current_logs:
        return new_logs
    return current_logs + new_logs



class OrchestrationState(TypedDict):
    user_input: str
    results: Annotated[dict, update_results]  # Dictionnaire accumulant les réponses { "nom_agent": "reponse" }
    supervisor_logs: Annotated[list, update_logs]
    next_agent: str  # Le nom du prochain agent à appeler, ou "reconstructeur"
    task_for_agent: str  # Le prompt spécifique généré par le superviseur pour ce spécialiste
    final_response: str  # La réponse finale pour l'utilisateur
    niveau_recherche: int   # 1, 2 ou 3 — nombre max d'appels LLM par sous-tâche
    current_task_calls: int # nombre d'appels faits pour la sous-tâche en cours
    current_task_agent: str # nom du spécialiste en cours de raffinement
    documents_generated: Annotated[list, update_logs]
    parallel_tasks: list

# --- 2. Fonction de construction ---
def build_orchestration_graph(agent_superviseur, agents_specialistes: list, agent_reconstructeur, niveau_recherche: int = 1):
    """
    Construit le graphe LangGraph.
    Hypothèse: tes agents ont un attribut 'nom' et une méthode 'executer_prompt'.
    """
    workflow = StateGraph(OrchestrationState)

    # --- Nœud du Superviseur ---
    def _decrire_specialistes(agents):
        """Construit une description enrichie : nom + rôle + MCP si connecté."""
        lignes = []
        for a in agents:
            desc = f"- {a.nom}"
            role = getattr(a, "prompt", "") or ""
            if role:
                desc += f" (rôle : {role[:120]})"
            mcp = getattr(a, "mcp", None)
            if mcp is not None:
                caps = ", ".join(mcp.capabilities) or "aucune"
                desc += (
                    f" — CONNECTÉ au MCP « {mcp.name} » ({mcp.mcp}) avec le token "
                    f"personnel de l'utilisateur. Capacités : {caps}."
                )
            lignes.append(desc)
        return "\n".join(lignes)

    def superviseur_node(state: OrchestrationState):
        noms_specialistes = [a.nom for a in agents_specialistes]
        desc_specialistes = _decrire_specialistes(agents_specialistes)
        resultats_actuels = state.get('results', {})
        niveau = state.get('niveau_recherche', niveau_recherche)
        task_calls = state.get('current_task_calls', 0)
        task_agent = state.get('current_task_agent', '')
        print(f"\n[SUPERVISEUR] Analyse en cours... résultats déjà obtenus : {list(resultats_actuels.keys())}")

        # Anti-boucle : si tous les agents ont répondu et assez de cycles → reconstructeur
        if len(resultats_actuels) >= len(noms_specialistes) and len(noms_specialistes) > 0:
            print(f"[SUPERVISEUR] Tous les agents ont répondu → reconstructeur")
            return {
                "next_agent": "reconstructeur",
                "task_for_agent": "",
                "current_task_calls": 0,
                "current_task_agent": "",
                "parallel_tasks": [],
                "supervisor_logs": [],
            }

        en_mode_raffinement = (
            niveau > 1
            and task_calls >= 1
            and task_agent in resultats_actuels
            and task_calls < niveau
        )

        if en_mode_raffinement:
            prompt_sup = (
                f"Tâche initiale de l'utilisateur : {state['user_input']}\n"
                f"Résultats obtenus jusqu'à présent : {resultats_actuels}\n"
                f"Agents disponibles (noms exacts à utiliser dans next_agent) : {noms_specialistes}\n"
                f"Détails des agents :\n{desc_specialistes}\n\n"
                f"CONTEXTE DE RAFFINEMENT — agent actuel : {task_agent}\n"
                f"Appels utilisés pour cette sous-tâche : {task_calls}/{niveau}\n"
                f"Si le résultat de '{task_agent}' est satisfaisant, passe à la prochaine sous-tâche ou route vers 'reconstructeur'. "
                f"Si le résultat est insuffisant, renvoie un prompt amélioré au MÊME agent '{task_agent}'. "
                "Réponds STRICTEMENT avec un JSON : "
                '{"next_agent": "nom_du_specialiste_ou_reconstructeur", "prompt": "instructions"}.'
            )
        else:
            prompt_sup = (
                f"Tâche initiale de l'utilisateur : {state['user_input']}\n"
                f"Résultats obtenus jusqu'à présent : {resultats_actuels}\n"
                f"Agents disponibles (noms exacts à utiliser dans next_agent) : {noms_specialistes}\n"
                f"Détails des agents :\n{desc_specialistes}\n\n"
                "Quand un agent est CONNECTÉ à un MCP avec le token personnel de l'utilisateur, "
                "toute demande relevant de ce service concerne le compte de l'utilisateur courant : "
                "ne demande JAMAIS son identifiant/username, donne directement la sous-tâche à l'agent.\n\n"
                "Analyse ce qui manque. Tu as deux options :\n\n"
                "OPTION 1 — Un seul agent (séquentiel) :\n"
                '{"next_agent": "nom_du_specialiste", "prompt": "instructions_pour_lui"}\n\n'
                "OPTION 2 — Plusieurs agents en parallèle (UNIQUEMENT si les tâches sont "
                "INDÉPENDANTES et ne dépendent pas l'une de l'autre) :\n"
                '{"parallel": [{"agent": "nom_agent_1", "prompt": "instructions_1"}, '
                '{"agent": "nom_agent_2", "prompt": "instructions_2"}]}\n\n'
                "Si toutes les sous-tâches sont finies, réponds : "
                '{"next_agent": "reconstructeur", "prompt": ""}.'
            )

        response = agent_superviseur.executer_prompt(prompt_sup)
        print(f"[SUPERVISEUR] Décision brute : {response.content[:500]}")

        # Parse la réponse JSON du superviseur
        try:
            decision = extraire_json(response.content)
            # Mode parallèle
            if "parallel" in decision and isinstance(decision["parallel"], list) and len(decision["parallel"]) > 1:
                parallel_tasks = decision["parallel"]
                valid_tasks = [t for t in parallel_tasks if
                               t.get("agent") in noms_specialistes and t.get("prompt", "").strip()]

                if len(valid_tasks) > 1:
                    agents_noms = [t["agent"] for t in valid_tasks]
                    print(f"[SUPERVISEUR] → Mode PARALLÈLE : {agents_noms}")
                    logs = []
                    for t in valid_tasks:
                        logs.append(f"→ {t['agent']} : {t['prompt']}")
                    return {
                        "next_agent": "__parallel__",
                        "task_for_agent": "",
                        "parallel_tasks": valid_tasks,
                        "current_task_calls": 0,
                        "current_task_agent": "",
                        "supervisor_logs": logs,
                    }
                elif len(valid_tasks) == 1:
                    decision = {"next_agent": valid_tasks[0]["agent"], "prompt": valid_tasks[0]["prompt"]}
                    # Mode séquentiel
            chosen_agent = decision['next_agent']

            # Hard-cap : le LLM ignore le plafond → forcer reconstructeur
            if chosen_agent == task_agent and task_calls >= niveau:
                print(f"[SUPERVISEUR] ⚠ Hard-cap atteint ({task_calls}/{niveau}) → forcé vers reconstructeur")
                chosen_agent = "reconstructeur"
                decision['next_agent'] = "reconstructeur"
                decision['prompt'] = ""

            # Gestion du compteur
            if chosen_agent == "reconstructeur":
                new_calls = 0
                new_agent = ""
            elif chosen_agent == task_agent:
                new_calls = task_calls + 1
                new_agent = task_agent
            else:
                new_calls = 1
                new_agent = chosen_agent

            print(f"[SUPERVISEUR] → Route vers : {chosen_agent} (appels sous-tâche : {new_calls}/{niveau})")
            return {
                "next_agent": chosen_agent,
                "task_for_agent": decision.get("prompt", ""),
                "current_task_calls": new_calls,
                "current_task_agent": new_agent,
                "parallel_tasks": [],
                "supervisor_logs": [f"→ {chosen_agent} : {decision['prompt']}"],
            }
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[SUPERVISEUR] ⚠ Parsing JSON échoué ({e}) → fallback reconstructeur")
            return {"next_agent": "reconstructeur", "task_for_agent": "", "current_task_calls": 0, "current_task_agent": "", "parallel_tasks": []}

    workflow.add_node("superviseur", superviseur_node)

    # --- Nœuds des Spécialistes ---
    # Fonction factory pour éviter le problème de late binding de Python dans les boucles
    def create_specialist_node(agent):
        def node(state: OrchestrationState):
            print(f"\n[{agent.nom.upper()}] Exécution en cours...")

            task = state.get("task_for_agent", "")
            for pt in state.get("parallel_tasks", []):
                if pt.get("agent") == agent.nom:
                    task = pt["prompt"]
                    break

            response = agent.executer_prompt(
                task,
                user_input_context=state.get("user_input", ""),
            )

            print(f"[{agent.nom.upper()}] Réponse reçue ({len(response.content)} caractères)")

            result = {
                "results": {agent.nom: response.content},
                "supervisor_logs": [f"{agent.nom} a répondu"]
            }

            # NOUVEAU : si l'agent doit générer un document
            if getattr(agent, "generate_document", False):
                try:
                    nom_fichier = generer_docx(
                        contenu_markdown=response.content,  # le texte de l'agent
                        titre=f"Document généré par {agent.nom}",
                        prefix=agent.nom.replace(" ", "_").lower()
                    )
                    result["documents_generated"] = [{
                        "agent": agent.nom,
                        "filename": nom_fichier
                    }]
                    result["supervisor_logs"].append(f"📄 {agent.nom} a généré le document : {nom_fichier}")
                except Exception as e:
                    print(f"Erreur génération document : {e}")

            return result

        return node

    for specialiste in agents_specialistes:
        workflow.add_node(specialiste.nom, create_specialist_node(specialiste))

    # --- Nœud du Reconstructeur ---
    def reconstructeur_node(state: OrchestrationState):
        print(f"\n[RECONSTRUCTEUR] Synthèse des résultats de : {list(state['results'].keys())}")

        docs = state.get("documents_generated", [])
        if docs:
            print(f"[RECONSTRUCTEUR] Document(s) généré(s) — synthèse courte")
            agents_sans_doc = {nom: rep for nom, rep in state['results'].items()
                               if not any(d['agent'] == nom for d in docs)}
            agents_avec_doc = [d['agent'] for d in docs]

            if agents_sans_doc:
                prompt_rec = (
                    f"Demande initiale : {state['user_input']}\n"
                    f"Résultats des agents : {agents_sans_doc}\n\n"
                    "Fais une synthèse UNIQUEMENT des résultats ci-dessus. "
                    "Ne reproduis PAS le contenu des documents générés. "
                    f"Mentionne simplement qu'un document Word a été généré par {', '.join(agents_avec_doc)} "
                    "et est disponible en téléchargement. "
                    "IMPORTANT : réponds dans la même langue que la demande initiale."
                )
                response = agent_reconstructeur.executer_prompt(prompt_rec)
                print(f"[RECONSTRUCTEUR] Réponse finale générée ({len(response.content)} caractères)")
                return {
                    "final_response": response.content,
                    "supervisor_logs": []
                }
            else:
                print(f"[RECONSTRUCTEUR] Tous les agents ont généré des documents → pas de synthèse")
                return {
                    "final_response": "",
                    "supervisor_logs": []
                }
        prompt_rec = (
            f"Demande initiale : {state['user_input']}\n"
            f"Données brutes des spécialistes : {state['results']}\n\n"
            "Structurise la réponse finale pour une bonne mise en forme. "
            "IMPORTANT : tu dois répondre OBLIGATOIREMENT dans la même langue que la demande initiale de l'utilisateur."
        )
        response = agent_reconstructeur.executer_prompt(prompt_rec)
        print(f"[RECONSTRUCTEUR] Réponse finale générée ({len(response.content)} caractères)")
        return {
            "final_response": response.content,
            "supervisor_logs": [
                "Reconstruction en cours...",
                "Reconstruction finale terminée"
            ]
        }

    workflow.add_node("reconstructeur", reconstructeur_node)

    # --- Configuration du Routing (Les Edges) ---
    workflow.set_entry_point("superviseur")

    # Fonction de routage conditionnel
    def route_from_supervisor(state: OrchestrationState):
        if state.get("next_agent") == "__parallel__":
            parallel_tasks = state.get("parallel_tasks", [])
            if parallel_tasks:
                print(f"[ROUTING] Envoi parallèle vers : {[t['agent'] for t in parallel_tasks]}")
                return [
                    Send(task["agent"], {
                        "user_input": state["user_input"],
                        "task_for_agent": task["prompt"],
                        "parallel_tasks": parallel_tasks,
                        "results": state.get("results", {}),
                        "supervisor_logs": [],
                        "next_agent": "",
                        "final_response": "",
                        "niveau_recherche": state.get("niveau_recherche", 1),
                        "current_task_calls": 0,
                        "current_task_agent": "",
                        "documents_generated": [],
                        "parallel_tasks": [],
                    })
                    for task in parallel_tasks
                ]
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