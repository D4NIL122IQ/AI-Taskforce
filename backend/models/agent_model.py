from sqlalchemy import Column, Integer, String, Float, Text, DateTime, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
<<<<<<< HEAD:back/models/agent_model.py
from back.appDatabase.database import Base
=======
from backend.appDatabase import Base
>>>>>>> e2627ce3cc0265d58ec20149260718ceb174b63b:backend/models/agent_model.py


class AgentModel(Base):
    __tablename__ = "agent"

    id_agent      = Column(Integer, primary_key=True, autoincrement=True)
    nom           = Column(String(100), nullable=False)
    modele        = Column(String(50), nullable=False)
    temperature   = Column(Float, nullable=False, default=0.7)
    max_tokens    = Column(Integer, nullable=False, default=1024)
    system_prompt = Column(Text, nullable=True)
    date_creation = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    statut        = Column(String(20), default="ACTIF")
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)


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
            "statut IN ('ACTIF','INACTIF', 'INTERROMPU')",
            name="ck_agent_statut",
        ),
    )

    users = relationship("User", back_populates="agents")
    document      = relationship("Document", back_populates="agent", cascade="all, delete-orphan")
    etapes         = relationship("Etape",    back_populates="agent")
    superviseur_de = relationship(
        "Workflow",
        foreign_keys="[Workflow.superviseur_id]",
        back_populates="superviseur"
    )
