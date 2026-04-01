from backend.modeles.graphBuilder import build_orchestration_graph
from backend.modeles.Agent import Agent


class Orchestration:
    """
    Orchestre un workflow multi-agents basé sur un graphe LangGraph.

    Reçoit un superviseur et une liste de spécialistes, crée automatiquement
    un agent reconstructeur, puis construit le graphe d'exécution.

    Attributes:
        superviseur (Agent): Agent superviseur qui décompose et route les tâches.
        specialistes (list[Agent]): Agents spécialisés qui exécutent les sous-tâches.
        reconstructeur (Agent): Agent créé automatiquement pour synthétiser la réponse finale.
        graph: Graphe LangGraph compilé.

    Example:
        ```python
        orchestration = Orchestration(superviseur=sup, specialistes=[dev, tester])
        reponse = orchestration.executer("Crée une API REST en Python")
        print(reponse)
        ```
    """

    def __init__(self, superviseur: Agent, specialistes: list):
        """
        Initialise l'orchestration et compile le graphe LangGraph.

        Un agent reconstructeur est créé automatiquement à partir des paramètres
        du superviseur (modèle, température, max_token).

        Args:
            superviseur (Agent): Agent chargé de décomposer les tâches et de router
                vers les spécialistes.
            specialistes (list[Agent]): Liste des agents spécialisés disponibles.
        """
        self.superviseur = superviseur
        self.specialistes = specialistes

        # Création automatique du reconstructeur avec les paramètres du superviseur
        self.reconstructeur = Agent(
            nom="reconstructeur",
            modele=superviseur.modele,
            prompt=(
                "Tu es un rédacteur expert. "
                "Tu reçois les résultats bruts des agents spécialistes et tu les transformes "
                "en une réponse finale claire, fluide et bien formatée pour l'utilisateur. "
                "Tu réponds TOUJOURS dans la même langue que la demande initiale de l'utilisateur."
            ),
            max_token=superviseur.max_token,
            temperature=0.5
        )

        self.graph = build_orchestration_graph(
            agent_superviseur=self.superviseur,
            agents_specialistes=self.specialistes,
            agent_reconstructeur=self.reconstructeur
        )

    def executer(self, prompt: str) -> str:
        """
        Lance l'orchestration pour une requête utilisateur.

        Args:
            prompt (str): La demande initiale de l'utilisateur.

        Returns:
            str: La réponse finale synthétisée par le reconstructeur.

        Example:
            ```python
            reponse = orchestration.executer("Explique les design patterns en Python")
            print(reponse)
            ```
        """
        initial_state = {
            "user_input": prompt,
            "results": {},
            "next_agent": "",
            "task_for_agent": "",
            "final_response": ""
        }

        final_state = self.graph.invoke(initial_state, config={"recursion_limit": 50})

        return final_state.get("final_response", "Erreur : Aucune réponse finale générée.")

    def afficher_graphe(self, chemin_image="graph.png"):
        """
        Sauvegarde une représentation visuelle du graphe en PNG.

        Args:
            chemin_image (str): Chemin du fichier image de sortie. Par défaut "graph.png".
        """
        try:
            image_data = self.graph.get_graph().draw_mermaid_png()
            with open(chemin_image, "wb") as f:
                f.write(image_data)
            print(f"Graphique sauvegardé sous {chemin_image}")
        except Exception as e:
            print(f"Impossible de dessiner le graphe : {e}")