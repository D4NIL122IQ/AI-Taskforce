from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.appDatabase.database import Base
from sqlalchemy.dialects.postgresql import UUID
from backend.models.execution_model import Execution

class Workflow(Base):
    __tablename__ = "workflow"

    id_workflow         = Column(Integer,     primary_key=True, autoincrement=True)
    nom                 = Column(String(100), nullable=False)
    donnees_graphe_json = Column(JSON,        nullable=True)
    superviseur_id      = Column(Integer,     ForeignKey("agent.id_agent"), nullable=True)
    date_creation       = Column(DateTime,    default=lambda: datetime.now(timezone.utc))
    utilisateur_id = Column(UUID(as_uuid=True), nullable=True)

    superviseur = relationship("Agent", foreign_keys=[superviseur_id])
    executions  = relationship("Execution", back_populates="workflow",
                               cascade="all, delete-orphan")
    mcp_tokens = relationship("McpToken", back_populates="workflow",cascade="all, delete-orphan")