from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_deepseek.chat_models import ChatDeepSeek
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.tools import tool
from back.logic.Message import Message
from datetime import datetime as dt

from dataclasses import dataclass

@dataclass
class LLMConfig:
    temperature: float
    max_token: int
    modele: str

@tool
def get_current_datetime():
    """
    Retourne la date et l'heure actuelles.
    """
    return dt.now().strftime("%Y-%m-%d %H:%M:%S")

class llmFactory:
    """
    Factory permettant d'initialiser différents modèles de langage (LLM)
    en fonction du fournisseur choisi.

    Cette classe centralise la création des LLM afin de :
    - uniformiser leur configuration
    - faciliter le changement de provider
    - rendre le code plus maintenable et extensible

    Modèles supportés :
    - OpenAI (GPT)
    - Google (Gemini)
    - Ollama 
    - Mistral
    - DeepSeek
    - Anthropic (Claude)

    Exemple :
        llm = LLMFactory.initialise_llm(config)
    """

    @staticmethod
    def initialise_llm(config:LLMConfig):
        """
        Initialise et retourne un modèle de langage selon le type demandé.

        Args:
            config (dataClasse): Objet contenant les paramètres du modèle :
                - temperature (float)
                - max_token (int)
                - modele (string): Type du modèle à utiliser.
                    Valeurs possibles :
                    - "OpenAI"
                    - "Gemini"
                    - "Ollama"
                    - "Mistral"
                    - "DeepSeek"
                    - "Anthropic"

        Returns:
            BaseChatModel: Instance du modèle LangChain configuré.

        Raises:
            ValueError: Si le modèle demandé n'est pas supporté.
        """

        if not config.modele:
            raise ValueError("Le type de modèle doit être spécifié")

        type_modele = config.modele.lower()

        if type_modele == "gemini":
            return ChatGoogleGenerativeAI(
                model="gemini-3-flash-preview",
                temperature=config.temperature,
                max_tokens=config.max_token
            )
        
        elif type_modele == "openai":
            return ChatOpenAI(
                model="gpt-4o-mini",
                temperature=config.temperature,
                max_tokens=config.max_token
            )

        elif type_modele == "ollama":
            return ChatOllama(
                model="llama3.2",
                temperature=config.temperature,
                max_tokens=config.max_token
            )

        elif type_modele == "mistral":
            return ChatMistralAI(
                model="mistral-medium",
                temperature=config.temperature,
                max_tokens=config.max_token
            )
        
        elif type_modele == "deepseek":
            return ChatDeepSeek(
                model="deepseek-chat",
                temperature=config.temperature,
                max_tokens=config.max_token,
                timeout=None,
                max_retries=2
            )
        
        elif type_modele == "anthropic":
            return ChatAnthropic(
                model="claude-3-haiku-20240307",
                temperature=config.temperature,
                max_tokens=config.max_token
            )

        else:
            raise ValueError(f"Modèle non supporté : {type_modele}")