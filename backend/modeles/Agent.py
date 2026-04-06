from datetime import datetime as dt
import os

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return False

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from backend.modeles.requestLLM import chat, MODEL as PLEIADE_MODEL

load_dotenv()


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

    Example:
        ```python
        agent = Agent(
            nom="Assistant",
            modele="Openai",
            prompt="Tu es un assistant spécialisé en finance.",
            max_token=1024,
            temperature=0.7
        )

        reponse = agent.executer_prompt("Explique-moi les ETF en 3 lignes.")
        print(reponse)

        # Enrichir avec un document
        agent.ajouter_document("rapport_annuel.pdf")

        # Changer dynamiquement le modèle
        agent.modele = "Mistral"
        ```
    """

    ctr = 0  # Compteur global pour générer des identifiants uniques

    def __init__(self, nom, modele, prompt, max_token,  temperature):
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

        Raises:
            ValueError: Si `nom` est vide ou n'est pas une chaîne.
            ValueError: Si `modele` n'est pas dans la liste des fournisseurs supportés.
            ValueError: Si `prompt` est vide ou n'est pas une chaîne.
            ValueError: Si `max_token` n'est pas un entier positif ≤ 8192.
            ValueError: Si `temperature` n'est pas un nombre entre 0 et 1.

        Example:
            ```python
            agent = Agent(
                nom="Analyste",
                modele="Mistral",
                prompt="Tu es un expert en cybersécurité.",
                max_token=2048,
                temperature=0.3
            )
            ```
        """

        self.valider_parametres(nom, modele, prompt, max_token, temperature)

        self.ID = Agent.ctr
        self.nom = nom
        self._modele = modele
        self._temperature = temperature
        self._max_token = max_token
        self.prompt = prompt
        self.date_creation = dt.now()
        self.documents = []


        self.ctr += 1

        # Template de prompt utilisé pour les interactions avec le LLM
        self.template = ChatPromptTemplate.from_messages([
            (
                "system",
                "Tu es {name}, un agent intelligent dont le rôle est : {role}. "
                "Tu dois fournir des réponses claires, précises et utiles. "
                "Si une information est incertaine, indique-le explicitement. "
                "Adapte ton niveau de détail en fonction de la demande."
                "Repond dans la meme langue que la langue du prompt"
            ),
            MessagesPlaceholder(variable_name="messages"),
        ])

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

    def executer_prompt(self, message, model=None):
        """
        Envoie un message à l'agent via l'API Pléiade, enrichi du contexte RAG
        si des documents ont été indexés pour cet agent.

        Args:
            message (str): Texte à envoyer. Ne doit pas être vide.
            model (str | None): Modèle Pléiade. Si None → PLEIADE_MODEL.

        Returns:
            SimpleNamespace avec attribut .content (str).
        """
        if not message.strip():
            raise ValueError("prompt vide")

        if model is None:
            from backend.modeles.requestLLM import MODEL as PLEIADE_MODEL
            model = PLEIADE_MODEL

        # ── Enrichissement RAG (optionnel) ───────────────────────────────────────
        # Si l'agent a des documents indexés, on cherche les chunks pertinents
        # et on les injecte avant la question dans le prompt système.
        contexte_rag = ""
        try:
            from backend.services.rag_service import RAGService
            rag = RAGService()
            contexte_rag = rag.contexte_pour_prompt(
                agent_id=self.ID,
                question=message,
                top_k=5
            )
        except Exception as e:
            # Ne jamais bloquer executer_prompt si le RAG échoue
            print(f"[Agent] ⚠ RAG indisponible : {e}")

        # ── Construction du prompt final ─────────────────────────────────────────
        from backend.modeles.requestLLM import chat

        prompt_text = (
            f"system: Tu es {self.nom}, un agent intelligent dont le rôle est : {self.prompt}. "
            "Tu dois fournir des réponses claires, précises et utiles. "
            "Si une information est incertaine, indique-le explicitement. "
            "Réponds dans la même langue que le prompt suivant."
        )

        # Injecter le contexte RAG s'il existe
        if contexte_rag:
            prompt_text += f"\n\n{contexte_rag}"

        prompt_text += f"\n\nQuestion : {message}"

        from types import SimpleNamespace
        result = chat(prompt_text, model)
        return SimpleNamespace(content=result)

    ##def executer_prompt(self, message, model=None):
        """
        Envoie un message à l'agent via l'API Pléiade et retourne la réponse.

        Args:
            message (str): Texte à envoyer à l'agent. Ne doit pas être vide.
            model (str | None): Modèle Pléiade à utiliser. Si None, utilise le
                modèle par défaut défini dans requestLLM (PLEIADE_MODEL).

        Returns:
            Objet avec attribut `.content` (str).
        """
        if not message.strip():
            raise ValueError("prompt vide")

        if model is None:
            model = PLEIADE_MODEL

        prompt_text = (
            f"system: Tu es {self.nom}, un agent intelligent dont le rôle est : {self.prompt}. "
            "Tu dois fournir des réponses claires, précises et utiles. "
            "Si une information est incertaine, indique-le explicitement. "
            "Réponds dans la même langue que le prompt suivant : "
            + message
        )
        from types import SimpleNamespace
        result = chat(prompt_text, model)
        return SimpleNamespace(content=result)



    def ajouter_document(self, filepath):
        """
        Enrichit le contexte de l'agent avec le contenu d'un fichier externe.

        Le contenu extrait est concaténé au `prompt` de l'agent, ce qui permet
        au LLM de s'appuyer sur ce document lors des prochains appels à
        `executer_prompt`.

        Formats supportés :

        | Extension | Librairie utilisée |
        |-----------|-------------------|
        | `.txt`    | built-in Python   |
        | `.pdf`    | PyPDF2            |
        | `.csv`    | pandas            |

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
