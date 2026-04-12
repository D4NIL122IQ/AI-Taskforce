# backend/models/mcp_token_model.py
"""
Modèle SQLAlchemy pour stocker les tokens OAuth MCP d'un workflow.

TABLE : mcp_token

  Chaque ligne = les credentials OAuth d'un workflow pour un provider MCP donné.
  Clé unique sur (workflow_id, mcp_type) : un workflow peut avoir
  GitHub ET Gmail simultanément, mais pas deux tokens GitHub.

CYCLE DE VIE :
  1. Création   : POST /executions/{workflow_id}/mcp-token
                  Appelé par le frontend après le flux OAuth MCP.
  2. Lecture    : McpTokenService.connecter_agent_mcp() avant l'exécution.
  3. Refresh    : McpTokenService._rafraichir_token() si l'API MCP retourne 401.
                  Met à jour access_token + refresh_token en base.
  4. Suppression: en cascade si le workflow est supprimé (ondelete="CASCADE").

À AJOUTER dans workflow_model.py :
  mcp_tokens = relationship(
      "McpToken",
      back_populates="workflow",
      cascade="all, delete-orphan"
  )
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text,
    DateTime, ForeignKey, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from backend.appDatabase.database import Base


class McpToken(Base):
    """
    Tokens OAuth MCP pour un workflow + provider.

    Attributes:
        id            (int):  Clé primaire auto-incrémentée.
        workflow_id   (int):  FK → workflow.id_workflow (suppression en cascade).
        mcp_type      (str):  "github" | "gmail" (doit être dans SUPPORTED_MCPS).
        token_public  (str):  Client ID / clé publique OAuth.
                              Requis par connect_mcp(token_public, token_tempo, mcp).
        access_token  (str):  Token court (expire en ~1h).
        refresh_token (str):  Token long pour renouveler l'access_token.
        created_at    (datetime): Horodatage de création (auto).
        updated_at    (datetime): Horodatage de dernière mise à jour (auto).
    """

    __tablename__ = "mcp_token"

    id = Column(Integer, primary_key=True, autoincrement=True)

    workflow_id = Column(
        Integer,
        ForeignKey("workflow.id_workflow", ondelete="CASCADE"),
        nullable=False,
    )

    # "github" | "gmail" — cohérent avec SUPPORTED_MCPS dans connect_mcp.py
    mcp_type = Column(String(50), nullable=False)

    # Text (pas String) : les JWT dépassent souvent 255 caractères
    token_public  = Column(Text, nullable=False)
    access_token  = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Un seul token par (workflow, provider)
    __table_args__ = (
        UniqueConstraint(
            "workflow_id", "mcp_type",
            name="uq_mcp_token_workflow_type",
        ),
    )

    workflow = relationship("Workflow", back_populates="mcp_tokens")

    def __repr__(self):
        return (
            f"<McpToken workflow_id={self.workflow_id} "
            f"mcp_type='{self.mcp_type}' updated_at={self.updated_at}>"
        )