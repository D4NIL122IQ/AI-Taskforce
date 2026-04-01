from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from backend.database import Base

TYPES_VALIDES = {"user_input", "agent_response", "system"}


class Message(Base):
    __tablename__ = "message"

    id            = Column(Integer,     primary_key=True, autoincrement=True)
    contenu       = Column(Text,        nullable=False)
    date_creation = Column(DateTime,    default=lambda: datetime.now(timezone.utc))
    type          = Column(String(30),  nullable=False)
    expediteur    = Column(String(100), nullable=False)
    execution_id  = Column(Integer, ForeignKey("execution.id_execution"), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "type IN ('user_input','agent_response','system')",
            name="ck_message_type"
        ),
    )
    execution = relationship("Execution", back_populates="messages")

    def __init__(self, contenu: str, type: str, expediteur: str,
                 date_creation: datetime = None):
        if not contenu:
            raise ValueError("Contenu vide")
        if type not in TYPES_VALIDES:
            raise ValueError(f"Type de message inconnu : {type}")

        self.contenu       = contenu
        self.type          = type
        self.expediteur    = expediteur
        self.date_creation = date_creation or datetime.now(timezone.utc)
        self.execution_id  = None

    def getContenu(self) -> str:
        return self.contenu

    def getDateCreation(self) -> datetime:
        return self.date_creation

    def toDict(self) -> dict:
        return {
            "id"           : self.id,
            "contenu"      : self.contenu,
            "date_creation": str(self.date_creation),
            "type"         : self.type,
            "expediteur"   : self.expediteur,
            "execution_id" : self.execution_id,
        }

    def __repr__(self):
        return f"<Message [{self.type}] de {self.expediteur}>"