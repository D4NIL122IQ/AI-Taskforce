# backend/models/mcp_token_model.py
"""
Tokens OAuth MCP d'un utilisateur (niveau utilisateur, pas workflow).

TABLE : mcp_token
  Chaque ligne = les credentials OAuth d'un utilisateur pour un provider MCP.
  Clé unique sur (utilisateur_id, mcp_type) : un utilisateur peut avoir
  GitHub ET Gmail, mais pas deux tokens GitHub.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from backend.appDatabase.database import Base


class McpToken(Base):
    __tablename__ = "mcp_token"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    utilisateur_id = Column(UUID(as_uuid=True), nullable=False)
    mcp_type       = Column(String(50), nullable=False)   # "github" | "gmail"
    token_public   = Column(Text, nullable=False)
    access_token   = Column(Text, nullable=False)
    refresh_token  = Column(Text, nullable=False)
    created_at     = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at     = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                            onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("utilisateur_id", "mcp_type", name="uq_mcp_token_user_type"),
    )

    def __repr__(self):
        return f"<McpToken user={self.utilisateur_id} mcp='{self.mcp_type}'>"
