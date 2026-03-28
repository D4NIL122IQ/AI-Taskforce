from sqlalchemy import Column, Integer, String, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from back.appDatabase.database import Base

STATUTS_VALIDES = {"EN_ATTENTE", "EN_COURS", "TERMINE", "ERREUR"}

# Machine Ã  Ã©tats finie (conception v2 Â§3.5.3)
TRANSITIONS_VALIDES = {
    "EN_ATTENTE": ["EN_COURS"],
    "EN_COURS":   ["TERMINE", "ERREUR"],
    "TERMINE":    [],               # Ã©tat terminal
    "ERREUR":     ["EN_ATTENTE"]    # retry possible
}


class Etape(Base):
    __tablename__ = "etape"

    id_etape          = Column(Integer,     primary_key=True, autoincrement=True)
    ordre_execution   = Column(Integer,     nullable=False)
    description_tache = Column(Text,        nullable=True)
    statut_etape      = Column(String(20),  nullable=False, default="EN_ATTENTE")
    agent_id          = Column(Integer,     ForeignKey("agent.id_agent"),    nullable=True)
    workflow_id       = Column(Integer,     ForeignKey("workflow.id_workflow"), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "ordre_execution >= 1",
            name="ck_etape_ordre"
        ),
        CheckConstraint(
            "statut_etape IN ('EN_ATTENTE','EN_COURS','TERMINE','ERREUR')",
            name="ck_etape_statut"
        ),
    )

    agent    = relationship("Agent",    back_populates="etapes")
    workflow = relationship("Workflow", back_populates="etapes")

