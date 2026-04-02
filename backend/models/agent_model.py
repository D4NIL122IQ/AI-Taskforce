from sqlalchemy import Column, Integer, String, Float, Text, DateTime, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.appDatabase.database import Base


class Agent(Base):
    __tablename__ = "agent"

    id_agent      = Column(Integer, primary_key=True, autoincrement=True)
    nom           = Column(String(100), nullable=False)
    role          = Column(Text, nullable=True)
    modele        = Column(String(50), nullable=False)
    temperature   = Column(Float, nullable=False, default=0.7)
    max_tokens    = Column(Integer, nullable=False, default=1024)
    system_prompt = Column(Text, nullable=True)
    date_creation = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    statut        = Column(String(20), default="ACTIF")
    utilisateur_id = Column(Integer, ForeignKey("utilisateur.id_utilisateur"), nullable=True)


    __table_args__ = (
        CheckConstraint(
            "modele IN ('Openai','Ollama','Mistral','DeepSeek','Anthropic','Gemini')",
            name="ck_agent_modele",
        ),

        CheckConstraint(
            "temperature >= 0.0 AND temperature <= 1.0",
            name="ck_agent_temperature",
        ),
        CheckConstraint(
            "max_tokens >= 1 AND max_tokens <= 8192",
            name="ck_agent_max_tokens",
        ),
        CheckConstraint(
            "statut IN ('ACTIF','INTERROMPU')",
            name="ck_agent_statut",
        ),
    )

    utilisateur = relationship("Utilisateur", back_populates="agents")
    documents      = relationship("Document", back_populates="agent", cascade="all, delete-orphan")
    etapes         = relationship("Etape",    back_populates="agent")
    superviseur_de = relationship(
        "Workflow",
        foreign_keys="[Workflow.superviseur_id]",
        back_populates="superviseur"
    )

