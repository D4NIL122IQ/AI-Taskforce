# backend/services/mcp_token_service.py
"""
McpTokenService — tokens OAuth MCP niveau utilisateur.

Un utilisateur connecte une fois GitHub ou Gmail.
Le token est stocké en BDD et réutilisé à chaque exécution.
"""

import os
import logging
from datetime import datetime, timezone

import requests
from sqlalchemy.orm import Session

from backend.models.mcp_token_model import McpToken
from backend.modeles.Agent import Agent as AgentLLM

logger = logging.getLogger(__name__)

REFRESH_URLS = {
    "github": os.getenv("MCP_GITHUB_REFRESH_URL", "https://github.com/login/oauth/access_token"),
    "gmail":  os.getenv("MCP_GMAIL_REFRESH_URL",  "https://oauth2.googleapis.com/token"),
}
MCP_CLIENT_ID     = os.getenv("MCP_CLIENT_ID", "")
MCP_CLIENT_SECRET = os.getenv("MCP_CLIENT_SECRET", "")
REQUEST_TIMEOUT   = 15


class McpTokenNotFoundError(Exception):
    pass


class McpTokenExpiredError(Exception):
    pass


class McpTokenService:

    def __init__(self, db: Session):
        self.db = db

    # ── Lecture ────────────────────────────────────────────────────────────────

    def get_tokens_for_user(self, utilisateur_id: str) -> list[McpToken]:
        return (
            self.db.query(McpToken)
            .filter(McpToken.utilisateur_id == utilisateur_id)
            .all()
        )

    def get_token(self, utilisateur_id: str, mcp_type: str) -> McpToken | None:
        return (
            self.db.query(McpToken)
            .filter(
                McpToken.utilisateur_id == utilisateur_id,
                McpToken.mcp_type == mcp_type,
            )
            .first()
        )

    # ── Création / mise à jour ─────────────────────────────────────────────────

    def creer_ou_remplacer(
        self,
        utilisateur_id: str,
        mcp_type: str,
        token_public: str,
        access_token: str,
        refresh_token: str,
    ) -> McpToken:
        existing = self.get_token(utilisateur_id, mcp_type)
        if existing:
            existing.token_public  = token_public
            existing.access_token  = access_token
            existing.refresh_token = refresh_token
            existing.updated_at    = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(existing)
            return existing

        token = McpToken(
            utilisateur_id=utilisateur_id,
            mcp_type=mcp_type,
            token_public=token_public,
            access_token=access_token,
            refresh_token=refresh_token,
        )
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    # ── Suppression ───────────────────────────────────────────────────────────

    def supprimer(self, utilisateur_id: str, mcp_type: str) -> bool:
        token = self.get_token(utilisateur_id, mcp_type)
        if not token:
            return False
        self.db.delete(token)
        self.db.commit()
        return True

    # ── Connexion agent (appelé par execution_router) ─────────────────────────

    def connecter_agent_mcp(
        self,
        agent: AgentLLM,
        utilisateur_id: str,
        mcp_type: str,
    ) -> None:
        """
        Connecte un agent à son MCP en utilisant le token de l'utilisateur.
        Rafraîchit automatiquement si le token est expiré.
        """
        token_db = self.get_token(utilisateur_id, mcp_type)
        if token_db is None:
            raise McpTokenNotFoundError(
                f"Aucun token MCP '{mcp_type}' pour l'utilisateur {utilisateur_id}."
            )

        try:
            agent.connecter_mcp(
                token_public=token_db.token_public,
                token_tempo=token_db.access_token,
                mcp=mcp_type,
            )
            return
        except Exception as e:
            err = str(e).lower()
            if "401" not in err and "unauthorized" not in err and "expired" not in err:
                raise

        # Token expiré → refresh
        logger.warning(f"[McpTokenService] Token expiré pour '{mcp_type}', refresh...")
        nouveaux = self._rafraichir_token(token_db)
        token_db.access_token  = nouveaux["access_token"]
        token_db.refresh_token = nouveaux["refresh_token"]
        token_db.updated_at    = datetime.now(timezone.utc)
        self.db.commit()

        try:
            agent.connecter_mcp(
                token_public=token_db.token_public,
                token_tempo=token_db.access_token,
                mcp=mcp_type,
            )
        except Exception as retry_err:
            raise McpTokenExpiredError(
                f"Connexion MCP '{mcp_type}' échouée après refresh : {retry_err}"
            ) from retry_err

    # ── Refresh OAuth ──────────────────────────────────────────────────────────

    def _rafraichir_token(self, token_db: McpToken) -> dict:
        url = REFRESH_URLS.get(token_db.mcp_type)
        if not url:
            raise McpTokenExpiredError(f"Aucune refresh URL pour '{token_db.mcp_type}'")

        resp = requests.post(
            url,
            data={
                "grant_type":    "refresh_token",
                "refresh_token": token_db.refresh_token,
                "client_id":     MCP_CLIENT_ID,
                "client_secret": MCP_CLIENT_SECRET,
            },
            headers={"Accept": "application/json"},
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            raise McpTokenExpiredError(f"Refresh échoué ({resp.status_code}): {resp.text}")

        data = resp.json()
        if "access_token" not in data:
            raise McpTokenExpiredError(f"Réponse OAuth invalide : {data}")

        return {
            "access_token":  data["access_token"],
            "refresh_token": data.get("refresh_token", token_db.refresh_token),
        }
