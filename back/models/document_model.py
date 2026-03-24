from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from back.appDatabase.database import Base

TYPES_VALIDES = {"pdf", "txt", "docx", "md"}


class Document(Base):
    __tablename__ = "document"

    id_document  = Column(Integer,      primary_key=True, autoincrement=True)
    nom_fichier  = Column(String(255),  nullable=False)
    type_fichier = Column(String(10),   nullable=False)
    chemin       = Column(Text,         nullable=False)
    date_upload  = Column(DateTime,     default=lambda: datetime.now(timezone.utc))
    agent_id     = Column(Integer,      ForeignKey("agent.id_agent"), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "type_fichier IN ('pdf','txt','docx','md')",
            name="ck_document_type_fichier"
        ),
    )

    agent = relationship("Agent", back_populates="documents")

    def __init__(self, nom_fichier: str, type_fichier: str, chemin: str,
                 agent_id: int, date_upload: datetime = None):
        if not nom_fichier:
            raise ValueError("Nom de fichier vide")
        if type_fichier not in TYPES_VALIDES:
            raise ValueError(f"Type de fichier non supporté : {type_fichier}")
        if not chemin:
            raise ValueError("Chemin vide")

        self.nom_fichier  = nom_fichier
        self.type_fichier = type_fichier
        self.chemin       = chemin
        self.agent_id     = agent_id
        self.date_upload  = date_upload or datetime.now(timezone.utc)