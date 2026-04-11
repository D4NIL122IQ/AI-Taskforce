from sqlalchemy import Column, Integer, String, Float, Text, DateTime, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.appDatabase.database import Base
from backend.models.document_model import Document
from sqlalchemy.dialects.postgresql import UUID
from backend.models.workflow_model import Workflow


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
    web_search    = Column(Integer, nullable=False, default=0)  # 0 = False, 1 = True
    utilisateur_id = Column(UUID(as_uuid=True), nullable=True)

    __table_args__ = (

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

    documents = relationship("Document", back_populates="agent", cascade="all, delete-orphan")
    superviseur_de = relationship(
        "Workflow",
        foreign_keys="[Workflow.superviseur_id]",
        back_populates="superviseur"
    )
