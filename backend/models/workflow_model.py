from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.appDatabase.database import Base
from backend.models.utilisateur_model import Utilisateur
from backend.models.etape_model import Etape
from backend.models.execution_model import Execution


class Workflow(Base):
    __tablename__ = "workflow"

    id_workflow         = Column(Integer,     primary_key=True, autoincrement=True)
    nom                 = Column(String(100), nullable=False)
    donnees_graphe_json = Column(JSON,        nullable=True)
    superviseur_id      = Column(Integer,     ForeignKey("agent.id_agent"), nullable=True)
    date_creation       = Column(DateTime,    default=lambda: datetime.now(timezone.utc))
    #status             = Column(String(20),  default="ACTIF")
    utilisateur_id      = Column(Integer, ForeignKey("utilisateur.id_utilisateur"), nullable=True)

    utilisateur = relationship("Utilisateur", back_populates="workflows")
    superviseur = relationship("Agent", foreign_keys=[superviseur_id])
    etapes      = relationship("Etape",     back_populates="workflow",
                               cascade="all, delete-orphan")
    executions  = relationship("Execution", back_populates="workflow",
                               cascade="all, delete-orphan")
