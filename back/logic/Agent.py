from datetime import datetime as dt
from dotenv import load_dotenv
import os

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import OllamaLLM, ChatOllama
from langchain_mistralai.chat_models import ChatMistralAI

from back.logic.Message import Message, MessageType

load_dotenv()


class Agent:
    ctr = 0

    def __init__(self, nom, modele, prompt, max_token,  temperature) :
        
        self.valider_parametres(nom, modele, prompt, max_token, temperature)
        
        self.ID = Agent.ctr
        self.nom = nom
        self._modele = modele
        self._temperature = temperature
        self._max_token = max_token
        self.prompt = prompt
        self.date_creation = dt.now()
        self.documents = []
        self.llm = self.initialise_llm(type_modele=modele)
        
        self.ctr +=1

        self.template = ChatPromptTemplate.from_messages([
            ("system", 
            "Ton nom est {name}. {role}. Suis avec rigueeur ces instructions"),
            MessagesPlaceholder(variable_name="messages"),
        ])

    def initialise_llm(self, type_modele):

        if type_modele == "Openai": 
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-pro", 
                temperature=self._temperature, 
                max_output_tokens=self._max_token,
            )
            
        elif type_modele == "Ollama":
            return ChatOllama(
                model="llama3",
                temperature=self._temperature
            )

        elif type_modele == "Mistral":
            return ChatMistralAI(
                model="mistral-medium",
                temperature=self._temperature,
                max_tokens=self._max_token
            )
        else:
            raise ValueError("Modèle non supporté")
        
    def valider_parametres(self, nom, modele, prompt, max_token, temperature):

        if not nom or not isinstance(nom, str):
            raise ValueError("Nom invalide")

        if modele not in ["Openai", "Ollama", "Mistral"]:
            raise ValueError("Modèle invalide")

        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt invalide")

        if not isinstance(max_token, int) or max_token <= 0 or max_token > 8192:
            raise ValueError("max_token invalide")

        if not isinstance(temperature, (int, float)) or not (0 <= temperature <= 1):
            raise ValueError("temperature invalide")
    
    def executer_prompt(self, message):
        if not message.strip():
            raise ValueError("prompt vide")

        agent = self.template | self.llm

        response = agent.invoke({
            "name": self.nom,
            "role": self.prompt,
            "messages": [("human", message)]   
        })
        
        message = Message(self, response.content, MessageType.AGENT, response.usage_metadata)
        
        return message

    def ajouter_document(self, filepath) :
        extension = os.path.splitext(filepath)[1].lower()

        content = ""

        if extension==".txt":
            with open(filepath, "r", encoding="utf-8" ) as reader:
                content = reader.read()

        elif extension==".pdf":
            from PyPDF2 import PdfReader
            reader = PdfReader(filepath)
            content =  "\n".join([page.extract_text() or "" for page in reader.pages])
        
        elif extension == ".csv":
            import pandas as pd
            content =  pd.read_csv(filepath).to_string()

        self.prompt += "voir plus de detail dans ce document : " + "\n" + content
        


    @property
    def modele(self):
        return self._modele

    @modele.setter
    def modele(self, value):
        self._modele = value
        self.llm = self.initialise_llm(self._modele)

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self._temperature = value
        self.llm = self.initialise_llm(self._modele)

    @property
    def max_token(self):
        return self._max_token

    @max_token.setter
    def max_token(self, value):
        self._max_token = value
        self.llm = self.initialise_llm(self._modele)




