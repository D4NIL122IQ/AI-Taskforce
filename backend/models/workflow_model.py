from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.appDatabase.database import Base


class Workflow(Base):
    __tablename__ = "workflow"

    id_workflow         = Column(Integer,     primary_key=True, autoincrement=True)
    nom                 = Column(String(100), nullable=False)
    donnees_graphe_json = Column(JSON,        nullable=True)
    superviseur_id      = Column(Integer,     ForeignKey("agent.id_agent"), nullable=True)
    date_creation       = Column(DateTime,    default=lambda: datetime.now(timezone.utc))
    utilisateur_id      = Column(Integer, ForeignKey("users.user_id"), nullable=True)

    users = relationship("User", back_populates="workflows")
    superviseur = relationship("AgentModel", foreign_keys=[superviseur_id])
    etapes      = relationship("Etape",     back_populates="workflow",
                               cascade="all, delete-orphan")
    executions  = relationship("Execution", back_populates="workflow",
                               cascade="all, delete-orphan")
