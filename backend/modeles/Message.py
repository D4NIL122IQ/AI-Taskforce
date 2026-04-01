from enum import Enum
from datetime import datetime as dt
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.modeles.Agent import Agent


class MessageType(Enum):
    """
    Représente les différents types de messages échangés dans le système.
    
    Attributes:
        USER: Message envoyé par un utilisateur.
        AGENT: Message généré par un agent.
        SYSTEM: Message interne au système.
    """
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class Message:
    """
    Représente un message échangé entre agents dans le système.

    Cette classe encapsule les informations essentielles d’un message,
    incluant l’émetteur, le contenu, le type et les métadonnées.

    Attributes:
        ctr_message (int): Compteur global pour générer des identifiants uniques.
        id (int): Identifiant unique du message.
        sender (Agent): Agent ayant envoyé le message.
        content (str): Contenu textuel du message.
        type (MessageType): Type du message (USER, AGENT, SYSTEM).
        date (datetime): Date et heure de création du message.
        metadata (dict): Informations supplémentaires liées au message.
    """

    ctr_message = 0

    def __init__(self, sender, content, message_type: MessageType, metadata: dict):
        """
        Initialise un nouveau message.

        Args:
            sender (Agent): L'agent émetteur du message.
            content (str): Le contenu du message.
            message_type (MessageType): Le type du message.
            metadata (dict): Métadonnées associées au message.

        Raises:
            ValueError: Si les paramètres fournis sont invalides.
        """

        self._valider_params(sender, content, message_type)

        self.id = Message.ctr_message
        Message.ctr_message += 1

        self.sender = sender
        self.content = content
        self.type = message_type
        self.date = dt.now()
        self.metadata = metadata or {}

    def _valider_params(self, sender, contenu, message_type: MessageType):
        """
        Valide les paramètres du message.

        Args:
            sender (Agent): L'agent émetteur.
            contenu (str): Le contenu du message.
            message_type (MessageType): Le type du message.

        Raises:
            ValueError: Si un paramètre est invalide.
        """

        if not contenu:
            raise ValueError("Message sans contenu")

        if not sender:
            raise ValueError("Sender invalide")

        if not isinstance(message_type, MessageType):
            raise ValueError("Type de message invalide")

    def to_dict(self):
        """
        Convertit le message en dictionnaire.

        Returns:
            dict: Représentation du message sous forme de dictionnaire.
        """
        return {
            "id": self.id,
            "sender": self.sender.nom,
            "content": self.content,
            "type": self.type.value,
            "date": self.date.isoformat(),
            "metadata": self.metadata
        }

    def getContenuMsg(self):
        """Retourne la reponse du llm uniquement"""
        return self.content

    def is_user_message(self):
        """
        Vérifie si le message provient d’un utilisateur.

        Returns:
            bool: True si le message est de type USER, sinon False.
        """
        return self.type == MessageType.USER

    def is_agent_message(self):
        """
        Vérifie si le message provient d’un agent.

        Returns:
            bool: True si le message est de type AGENT, sinon False.
        """
        return self.type == MessageType.AGENT

    def same_message(self, other):
        """
        Compare le contenu de deux messages.

        Args:
            other (Message): Un autre message à comparer.

        Returns:
            bool: True si les contenus sont identiques.
        """
        return self.content == other.content

    def __eq__(self, other):
        """
        Compare deux messages par leur identifiant.

        Args:
            other (Message): Un autre message.

        Returns:
            bool: True si les deux messages ont le même id.
        """
        return isinstance(other, Message) and self.id == other.id