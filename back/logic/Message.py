from enum import Enum
from datetime import datetime as dt
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from back.modeles.Agent import Agent


class MessageType(Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class Message:
    ctr_message = 0

    def __init__(self, sender, content, message_type: MessageType, metadata:dict):

        self._valider_params(sender, content, message_type)

        self.id = Message.ctr_message
        Message.ctr_message += 1

        self.sender = sender
        self.content = content
        self.type = message_type
        self.date = dt.now()
        self.metadata = metadata or {}

    def _valider_params(self, sender, contenu, message_type: MessageType):

        if not contenu :
            raise ValueError("Message sans contenu")

        if not sender:
            raise ValueError("Sender invalide")

        if not isinstance(message_type, MessageType):
            raise ValueError("Type de message invalide")
        
    def to_dict(self):
        return {
            "id": self.id,
            "sender": self.sender.nom,
            "content": self.content,
            "type": self.type.value,
            "date": self.date.isoformat(),
            "metadata": self.metadata
        }
    
    def is_user_message(self):
        return self.type == MessageType.USER

    def is_agent_message(self):
        return self.type == MessageType.AGENT
    
    def same_message(self, other):
        return self.content == other.content
    
    def __eq__(self, other):
        return isinstance(other, Message) and self.id == other.id