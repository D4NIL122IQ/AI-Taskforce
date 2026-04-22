from datetime import datetime as dt
import os

from backend.modeles.requestLLM import chat
from backend.mcp.connect_mcp import connect_mcp, MCPConnection, SUPPORTED_MCPS
from langfuse import observe


class Agent:
    """
    Représente un agent intelligent basé sur un modèle de langage (LLM).

    L'agent encapsule un modèle de langage configuré dynamiquement et expose
    une interface simple pour interagir avec lui via des messages texte.
    Il peut également enrichir son contexte avec des documents externes.

    Attributes:
        ID (int): Identifiant unique auto-incrémenté de l'agent.
        nom (str): Nom de l'agent, utilisé dans le template de prompt.
        prompt (str): Rôle ou instruction principale transmise au LLM.
        date_creation (datetime): Horodatage de la création de l'instance.
        documents (list): Liste des chemins de documents ajoutés à l'agent.
        llm: Instance du modèle LLM initialisée via `llmFactory`.
        template (ChatPromptTemplate): Template LangChain utilisé pour structurer les échanges.
        modele (str): Modèle LLM sélectionné (propriété avec setter).
        temperature (float): Niveau de créativité du modèle (propriété avec setter).
        max_token (int): Limite de tokens par réponse (propriété avec setter).

    Note:
        Chaque modification de `modele`, `temperature` ou `max_token` via leurs setters
        déclenche automatiquement une réinitialisation du modèle LLM sous-jacent.
    """

    def __init__(self, nom, modele, prompt, max_token,  temperature, ID: int = 0, use_web: bool =False, utilise_mcp: bool = False, generate_document: bool = False):
        """
        Initialise un agent avec ses paramètres principaux.

        Valide les paramètres, instancie le modèle LLM via `llmFactory`,
        et configure le template de prompt LangChain.

        Args:
            nom (str): Nom de l'agent (non vide).
            modele (str): Identifiant du fournisseur LLM. Valeurs acceptées :
                `"Openai"`, `"Ollama"`, `"Mistral"`, `"DeepSeek"`, `"Anthropic"`, `"Gemini"`.
            prompt (str): Instruction principale définissant le rôle de l'agent (non vide).
            max_token (int): Nombre maximum de tokens générés par réponse.
                Doit être un entier compris entre 1 et 8192.
            temperature (float): Niveau de créativité du modèle.
                Valeur comprise entre 0 (déterministe) et 1 (créatif).
            use_web (bool): Indique si l'agent a accès à Internet pour enrichir ses réponses.

        Raises:
            ValueError: Si `nom` est vide ou n'est pas une chaîne.
            ValueError: Si `modele` n'est pas dans la liste des fournisseurs supportés.
            ValueError: Si `prompt` est vide ou n'est pas une chaîne.
            ValueError: Si `max_token` n'est pas un entier positif ≤ 8192.
            ValueError: Si `temperature` n'est pas un nombre entre 0 et 1.
        """

        self.valider_parametres(nom, modele, prompt, max_token, temperature)

        self.ID = ID  # sera défini lors de l'insertion en base de données
        self.nom = nom
        self._modele = modele
        self._temperature = temperature
        self._max_token = max_token
        self.prompt = prompt
        self.use_web = use_web
        self.utilise_mcp = utilise_mcp
        self.generate_document = generate_document
        self.date_creation = dt.now()
        self.documents = []
        self._mcp: MCPConnection | None = None

    def valider_parametres(self, nom, modele, prompt, max_token, temperature):
        """
        Vérifie la validité des paramètres fournis lors de l'initialisation.

        Cette méthode est appelée automatiquement dans `__init__` et n'a pas
        vocation à être utilisée directement.

        Args:
            nom (str): Nom de l'agent.
            modele (str): Identifiant du fournisseur LLM.
            prompt (str): Instruction principale de l'agent.
            max_token (int): Limite de tokens (entre 1 et 8192).
            temperature (float): Créativité du modèle (entre 0 et 1).

        Raises:
            ValueError: Si `nom` est vide ou n'est pas une chaîne.
            ValueError: Si `modele` n'est pas dans la liste des fournisseurs supportés.
            ValueError: Si `prompt` est vide ou n'est pas une chaîne.
            ValueError: Si `max_token` n'est pas un entier positif ≤ 8192.
            ValueError: Si `temperature` n'est pas un nombre entre 0 et 1.
        """

        if not nom or not isinstance(nom, str):
            raise ValueError("Nom invalide")

        if not modele or not isinstance(modele, str):
            raise ValueError("Modèle invalide")

        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt invalide")

        if not isinstance(max_token, int) or max_token <= 0 or max_token > 8192:
            raise ValueError("max_token invalide")

        if not isinstance(temperature, (int, float)) or not (0 <= temperature <= 1):
            raise ValueError("temperature invalide")

    # def executer_prompt(self, message):
    #     """Version LangChain — conservée en commentaire pour référence."""
    #     if not message.strip():
    #         raise ValueError("prompt vide")
    #     agent = self.template | self.llm
    #     return agent.invoke({
    #         "name": self.nom,
    #         "role": self.prompt,
    #         "messages": [("human", message)]
    #     })

    # backend/modeles/Agent.py  — PATCH RAG
    """
    CHANGEMENT :
      - Si l'agent a des documents indexés (RAGService),
        le contexte pertinent est injecté automatiquement avant la question.
      - Si aucun document → comportement identique à avant (aucune régression).
    """

    @observe(name="executer_prompt")
    def executer_prompt(self, message, user_input_context: str = ""):
        """
        Envoie un message à l'agent via l'API Pléiade, enrichi du contexte RAG
        si des documents ont été indexés pour cet agent.

        Utilise le modèle, la température et le max_token configurés à l'initialisation.

        Args:
            message (str): Texte à envoyer. Ne doit pas être vide.

        Returns:
            SimpleNamespace avec attribut .content (str).
        """
        if not message.strip():
            raise ValueError("prompt vide")

        model = self._modele

        # ── Enrichissement RAG ──────────────────────────────────────
        contexte_rag = ""
        try:
            from backend.services.rag_service import RAGService
            contexte_rag = RAGService().contexte_pour_prompt(
                agent_id=self.ID,
                question=user_input_context,
                top_k=5
            )
            print(f"************Question reel de user : {user_input_context}")
            print(f"\n***********contexte_rag: {contexte_rag}")
        except Exception as e:
            print(f"[Agent] RAG indisponible : {e}")

        # ── Enrichissement MCP ────────────────────────────────────────
        contexte_mcp = ""
        print(f"[Agent:{self.nom}] mcp_actif={self.mcp_actif}")
        if self.mcp_actif:
            from backend.mcp.mcp_client import (
                detecter_outils_necessaires, appeler_outil_mcp,
                formater_resultats_mcp, MCPCallError
            )
            texte_detection = f"{user_input_context} {message}".strip()
            outils = detecter_outils_necessaires(texte_detection, self._mcp.capabilities)
            print(f"[Agent:{self.nom}] MCP outils détectés: {outils}")
            resultats_bruts = []
            for outil, params in outils:
                try:
                    print(f"[Agent:{self.nom}] Appel MCP → {outil}({params})")
                    res = appeler_outil_mcp(self._mcp, outil, params)
                    resultats_bruts.append((outil, res))
                    print(f"[Agent:{self.nom}] MCP {outil} OK — {len(str(res))} chars")
                except MCPCallError as e:
                    print(f"[Agent:{self.nom}] MCP {outil} ERREUR: {e}")
            if resultats_bruts:
                contexte_mcp = formater_resultats_mcp(resultats_bruts, self._mcp.name)
                print(f"[Agent:{self.nom}] Contexte MCP injecté ({len(contexte_mcp)} chars)")
            else:
                print(f"[Agent:{self.nom}] Aucun résultat MCP — contexte vide")

        # ── Construction du prompt final ─────────────────────────────────────────
        prompt_text = (
            f"system: Tu es {self.nom}, un agent intelligent dont le rôle est : {self.prompt}. "
            "Tu dois fournir des réponses claires, précises et utiles. "
            "En consulatant les informations de la recherche web si fournies"
            "Si une information est incertaine, indique-le explicitement. "
            "Réponds dans la même langue que le prompt suivant."
        )

        if contexte_rag:
            prompt_text += f"\n\n{contexte_rag}"

        if contexte_mcp:
            prompt_text += f"\n\n{contexte_mcp}"
        conv_history = [
            {"role": "system", "content": prompt_text}
        ]

        from types import SimpleNamespace
        result = chat(
            message, model,
            conversation_history=conv_history,
            web_search=self.use_web,
            temperature=self._temperature,
            max_tokens=self._max_token
        )
        return SimpleNamespace(content=result)




    def ajouter_document(self, filepath):
        """
        Enrichit le contexte de l'agent avec le contenu d'un fichier externe.

        Le contenu extrait est concaténé au `prompt` de l'agent, ce qui permet
        au LLM de s'appuyer sur ce document lors des prochains appels à
        `executer_prompt`.

        Formats supportés : pdf, txt, csv.
        Args:
            filepath (str): Chemin absolu ou relatif vers le fichier à charger.

        Warning:
            Les formats non listés ci-dessus sont silencieusement ignorés
            (aucune exception n'est levée, le prompt reste inchangé).

        Example:
            ```python
            agent.ajouter_document("data/contrat.pdf")
            agent.ajouter_document("data/clients.csv")
            agent.ajouter_document("notes.txt")
            ```
        """

        extension = os.path.splitext(filepath)[1].lower()
        content = ""

        if extension == ".txt":
            with open(filepath, "r", encoding="utf-8") as reader:
                content = reader.read()

        elif extension == ".pdf":
            from PyPDF2 import PdfReader
            reader = PdfReader(filepath)
            content = "\n".join([page.extract_text() or "" for page in reader.pages])

        elif extension == ".csv":
            import pandas as pd
            content = pd.read_csv(filepath).to_string()

        # Enrichissement du prompt avec le contenu du document
        self.prompt += "voir plus de detail dans ce document : " + "\n" + content

    # ── MCP ──────────────────────────────────────────────────────────────────

    def connecter_mcp(self, token_public: str, token_tempo: str, mcp: str) -> MCPConnection:
        """
        Connecte l'agent à un MCP et stocke la connexion.

        Un agent ne peut être connecté qu'à un seul MCP à la fois.
        Appeler cette méthode remplace toute connexion existante.

        Args:
            token_public (str): Token public / client ID (sera fourni par la BDD).
            token_tempo  (str): Token temporaire / access token (sera fourni par la BDD).
            mcp          (str): "github" ou "gmail".

        Returns:
            MCPConnection: La connexion active.

        Raises:
            ValueError: Si le MCP n'est pas supporté.
        """
        self._mcp = connect_mcp(token_public, token_tempo, mcp)
        return self._mcp

    def deconnecter_mcp(self) -> None:
        """Supprime la connexion MCP active de l'agent."""
        self._mcp = None

    def changer_mcp(self, token_public: str, token_tempo: str, mcp: str) -> MCPConnection:
        """
        Remplace la connexion MCP actuelle par une nouvelle.

        Équivalent à `deconnecter_mcp()` suivi de `connecter_mcp()`.

        Args:
            token_public (str): Token public du nouveau MCP.
            token_tempo  (str): Token temporaire du nouveau MCP.
            mcp          (str): "github" ou "gmail".

        Returns:
            MCPConnection: La nouvelle connexion active.
        """
        self.deconnecter_mcp()
        return self.connecter_mcp(token_public, token_tempo, mcp)

    @property
    def mcp(self) -> MCPConnection | None:
        """
        Connexion MCP active de l'agent, ou None si aucune.

        Returns:
            MCPConnection | None
        """
        return self._mcp

    @property
    def mcp_actif(self) -> bool:
        """True si l'agent est connecté à un MCP."""
        return self._mcp is not None

    @staticmethod
    def mcps_disponibles() -> set:
        """Retourne l'ensemble des MCPs supportés."""
        return SUPPORTED_MCPS

    # ── Propriétés LLM ───────────────────────────────────────────────────────

    @property
    def modele(self):
        """
        Modèle LLM actuel de l'agent.

        Returns:
            str: Identifiant du fournisseur LLM (ex: `"Openai"`, `"Mistral"`).

        Note:
            Modifier cette propriété réinitialise automatiquement `self.llm`.

        Example:
            ```python
            print(agent.modele)   # "Openai"
            agent.modele = "Mistral"  # réinitialise le LLM
            ```
        """
        return self._modele

    @modele.setter
    def modele(self, value):
        self._modele = value

    @property
    def temperature(self):
        """
        Température (créativité) actuelle du modèle.

        Returns:
            float: Valeur entre 0 (déterministe) et 1 (très créatif).

        Note:
            Modifier cette propriété réinitialise automatiquement `self.llm`.

        Example:
            ```python
            print(agent.temperature)   # 0.7
            agent.temperature = 0.2    # réinitialise le LLM
            ```
        """
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self._temperature = value

    @property
    def max_token(self):
        """
        Limite maximale de tokens par réponse.

        Returns:
            int: Nombre de tokens maximum (entre 1 et 8192).

        Note:
            Modifier cette propriété réinitialise automatiquement `self.llm`.

        Example:
            ```python
            print(agent.max_token)   # 1024
            agent.max_token = 4096   # réinitialise le LLM
            ```
        """
        return self._max_token

    @max_token.setter
    def max_token(self, value):
        self._max_token = value