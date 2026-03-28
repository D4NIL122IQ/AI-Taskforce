from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
from back.appDatabase.database import Base

STATUTS_VALIDES = {"EN_COURS", "TERMINE", "ERREUR"}


class Execution(Base):
    __tablename__ = "execution"

    id_execution   = Column(Integer,     primary_key=True, autoincrement=True)
    date_execution = Column(DateTime,    default=lambda: datetime.now(timezone.utc))
    status         = Column(String(20),  nullable=False, default="EN_COURS")
    # Historique complet de la boucle superviseur (sÃ©rialisÃ© en JSON)
    history_json   = Column(JSONB,       nullable=True)
    # Outputs finaux par agent : { agent_id: message_dict }
    outputs_json   = Column(JSONB,       nullable=True)
    workflow_id    = Column(Integer,     ForeignKey("workflow.id_workflow"), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('EN_COURS','TERMINE','ERREUR')",
            name="ck_execution_status"
        ),
    )

    # Relations
    workflow  = relationship("Workflow",  back_populates="executions")
    messages  = relationship("Message",   back_populates="execution",
                             cascade="all, delete-orphan",
                             order_by="Message.date_creation")
    resultat  = relationship("Resultat",  back_populates="execution",
                             uselist=False,   # 1 rÃ©sultat max par exÃ©cution
                             cascade="all, delete-orphan")

# ------------------------------------------------------------------
# Classe Resultat
# ------------------------------------------------------------------

from sqlalchemy import Text, UniqueConstraint


class Resultat(Base):
    __tablename__ = "resultat"

    id_resultat     = Column(Integer,   primary_key=True, autoincrement=True)
    contenu_final   = Column(Text,      nullable=False)
    date_generation = Column(DateTime,  default=lambda: datetime.now(timezone.utc))
    execution_id    = Column(Integer,   ForeignKey("execution.id_execution"),
                             nullable=False, unique=True)

    execution = relationship("Execution", back_populates="resultat")

