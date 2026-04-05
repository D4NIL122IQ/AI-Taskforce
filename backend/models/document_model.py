from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.appDatabase.database import Base

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

    agent = relationship("Agent", back_populates="document")