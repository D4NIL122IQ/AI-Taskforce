from datetime import datetime as dt
from dotenv import load_dotenv
import os

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from back.logic.LLMFactory import llmFactory, LLMConfig 

load_dotenv()


class Agent:
    """
    Représente un agent intelligent basé sur un modèle de langage (LLM).

    L'agent permet de :
    - générer des réponses à partir d'un prompt
    - configurer dynamiquement un modèle (LLM, température, tokens)
    - enrichir son contexte via des documents
    """

    ctr = 0  # Compteur global pour générer des identifiants uniques

    def __init__(self, nom, modele, prompt, max_token,  temperature):
        """
        Initialise un agent avec ses paramètres principaux.

        :param nom: nom de l'agent
        :param modele: type de modèle LLM à utiliser
        :param prompt: rôle ou instruction principale de l'agent
        :param max_token: nombre maximal de tokens générés
        :param temperature: niveau de créativité du modèle (0 à 1)
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

        # Initialisation du modèle via la factory
        self.llm = llmFactory.initialise_llm(
            LLMConfig(self.temperature,
                      self.max_token,
                      self.modele)
        )

        self.ctr += 1

        # Template de prompt utilisé pour les interactions avec le LLM
        self.template = ChatPromptTemplate.from_messages([
            (
                "system",
                "Tu es {name}, un agent intelligent dont le rôle est : {role}. "
                "Tu dois fournir des réponses claires, précises et utiles. "
                "Si une information est incertaine, indique-le explicitement. "
                "Adapte ton niveau de détail en fonction de la demande."
            ),
            MessagesPlaceholder(variable_name="messages"),
        ])

    def valider_parametres(self, nom, modele, prompt, max_token, temperature):
        """
        Vérifie la validité des paramètres fournis lors de l'initialisation.

        :raises ValueError: si un des paramètres est invalide
        """

        if not nom or not isinstance(nom, str):
            raise ValueError("Nom invalide")

        if modele not in ["Openai", "Ollama", "Mistral", "DeepSeek", "Anthropic", "Gemini"]:
            raise ValueError("Modèle invalide")

        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt invalide")

        if not isinstance(max_token, int) or max_token <= 0 or max_token > 8192:
            raise ValueError("max_token invalide")

        if not isinstance(temperature, (int, float)) or not (0 <= temperature <= 1):
            raise ValueError("temperature invalide")

    def executer_prompt(self, message):
        """
        Exécute un message utilisateur via le modèle LLM.

        :param message: texte à envoyer à l'agent
        :return: réponse générée par le LLM
        :raises ValueError: si le message est vide
        """

        if not message.strip():
            raise ValueError("prompt vide")

        # Composition du pipeline LangChain (template + modèle)
        agent = self.template | self.llm

        response = agent.invoke({
            "name": self.nom,
            "role": self.prompt,
            "messages": [("human", message)]
        })

        return response

    def ajouter_document(self, filepath):
        """
        Ajoute le contenu d’un document au prompt de l’agent.

        Formats supportés :
        - .txt
        - .pdf
        - .csv

        :param filepath: chemin vers le fichier à charger
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
        Retourne le modèle LLM actuel.
        """
        return self._modele

    @modele.setter
    def modele(self, value):
        """
        Met à jour le modèle LLM et réinitialise l'instance correspondante.
        """
        self._modele = value
        self.llm = llmFactory.initialise_llm(LLMConfig(self.temperature,
                        self.max_token,
                        self.modele))

    @property
    def temperature(self):
        """
        Retourne la température actuelle du modèle.
        """
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        """
        Met à jour la température et réinitialise le modèle LLM.
        """
        self._temperature = value
        self.llm = llmFactory.initialise_llm(LLMConfig(self.temperature,
                        self.max_token,
                        self.modele))

    @property
    def max_token(self):
        """
        Retourne le nombre maximal de tokens.
        """
        return self._max_token

    @max_token.setter
    def max_token(self, value):
        """
        Met à jour la limite de tokens et réinitialise le modèle LLM.
        """
        self._max_token = value
        self.llm = llmFactory.initialise_llm(LLMConfig(self.temperature,
                        self.max_token,
                        self.modele))