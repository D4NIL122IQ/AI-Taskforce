# backend/services/mcp_token_service.py
"""
McpTokenService — Gestion des tokens OAuth MCP (lecture, refresh, persistance).

RESPONSABILITÉS :
  1. Lire le McpToken depuis la BDD pour un (workflow_id, mcp_type).
  2. Appeler agent.connecter_mcp() avec les tokens stockés.
  3. Si connect_mcp() lève une erreur 401 (token expiré) :
       a. Appeler l'endpoint OAuth du provider pour rafraîchir les tokens.
       b. Mettre à jour access_token + refresh_token en base (SQLAlchemy).
       c. Reconnecter l'agent avec les nouveaux tokens.

CE SERVICE NE FAIT PAS :
  - Les appels métiers MCP réels → c'est MCPConnection (connect_mcp.py).
  - La création des agents          → c'est execution_router.

UTILISATION dans execution_router.py :
  from backend.services.mcp_token_service import McpTokenService

  svc = McpTokenService(db)
  svc.connecter_agent_mcp(agent, workflow_id="3", mcp_type="github")

VARIABLES D'ENVIRONNEMENT (.env) :
  MCP_GITHUB_REFRESH_URL=https://github.com/login/oauth/access_token
  MCP_GMAIL_REFRESH_URL=https://oauth2.googleapis.com/token
  MCP_CLIENT_ID=votre_client_id
  MCP_CLIENT_SECRET=votre_client_secret
"""

import os
import logging
from datetime import datetime, timezone

import requests
from sqlalchemy.orm import Session

from backend.models.mcp_token_model import McpToken
from backend.modeles.Agent import Agent as AgentLLM

logger = logging.getLogger(__name__)

# ── URLs de refresh par provider ──────────────────────────────────────────────
REFRESH_URLS = {
    "github": os.getenv(
        "MCP_GITHUB_REFRESH_URL",
        "https://github.com/login/oauth/access_token"
    ),
    "gmail": os.getenv(
        "MCP_GMAIL_REFRESH_URL",
        "https://oauth2.googleapis.com/token"
    ),
}
MCP_CLIENT_ID     = os.getenv("MCP_CLIENT_ID", "")
MCP_CLIENT_SECRET = os.getenv("MCP_CLIENT_SECRET", "")
REQUEST_TIMEOUT   = 15


class McpTokenNotFoundError(Exception):
    """Aucun token en BDD pour ce (workflow_id, mcp_type). Re-auth OAuth requise."""
    pass


class McpTokenExpiredError(Exception):
    """Le refresh_token est lui-même révoqué. Re-auth manuelle requise."""
    pass


class McpTokenService:
    """
    Service de gestion des tokens OAuth MCP.

    Args:
        db (Session): Session SQLAlchemy injectée par FastAPI via Depends(get_db).
    """

    def __init__(self, db: Session):
        self.db = db

    # ──────────────────────────────────────────────────────────────────────────
    # MÉTHODE PRINCIPALE — appelée par execution_router pour chaque agent MCP
    # ──────────────────────────────────────────────────────────────────────────

    def connecter_agent_mcp(
        self,
        agent: AgentLLM,
        workflow_id: int,
        mcp_type: str,
    ) -> None:
        """
        Connecte un agent à son MCP en utilisant les tokens stockés en BDD.

        Séquence complète :
          1. Lire McpToken en BDD pour (workflow_id, mcp_type).
          2. Appeler agent.connecter_mcp(token_public, access_token, mcp_type).
          3. Si erreur 401 détectée :
               a. _rafraichir_token() → appel OAuth du provider.
               b. _sauvegarder_tokens() → mise à jour BDD.
               c. Retry agent.connecter_mcp() avec le nouveau access_token.

        Args:
            agent       (AgentLLM): Instance Agent créée par execution_router.
            workflow_id (int):      ID du workflow en cours d'exécution.
            mcp_type    (str):      "github" | "gmail".

        Raises:
            McpTokenNotFoundError: Aucun token en BDD → l'utilisateur doit
                                   d'abord s'authentifier via le flux OAuth.
            McpTokenExpiredError:  refresh_token révoqué → re-auth manuelle.
        """
        token_db = self._lire_token(workflow_id, mcp_type)

        # ── Tentative 1 : access_token courant ───────────────────────────────
        try:
            agent.connecter_mcp(
                token_public=token_db.token_public,
                token_tempo=token_db.access_token,
                mcp=mcp_type,
            )
            logger.info(
                f"[McpTokenService] Agent '{agent.nom}' connecté à "
                f"'{mcp_type}' (workflow_id={workflow_id})."
            )
            return  # ← succès, on s'arrête ici

        except Exception as e:
            # Vérifier si c'est bien une erreur de token expiré
            err = str(e).lower()
            if "401" not in err and "unauthorized" not in err and "expired" not in err:
                raise  # Autre erreur → on la propage telle quelle

        # ── Token expiré → refresh ────────────────────────────────────────────
        logger.warning(
            f"[McpTokenService] Access token expiré pour '{mcp_type}' "
            f"(workflow_id={workflow_id}). Rafraîchissement OAuth..."
        )

        nouveaux_tokens = self._rafraichir_token(token_db)

        self._sauvegarder_tokens(
            token_db=token_db,
            nouveau_access=nouveaux_tokens["access_token"],
            nouveau_refresh=nouveaux_tokens["refresh_token"],
        )

        # ── Tentative 2 : nouveau access_token ───────────────────────────────
        try:
            agent.connecter_mcp(
                token_public=token_db.token_public,
                token_tempo=nouveaux_tokens["access_token"],
                mcp=mcp_type,
            )
            logger.info(
                f"[McpTokenService] Agent '{agent.nom}' reconnecté à "
                f"'{mcp_type}' après refresh (workflow_id={workflow_id})."
            )
        except Exception as retry_err:
            raise McpTokenExpiredError(
                f"Connexion MCP '{mcp_type}' échouée après refresh "
                f"(workflow_id={workflow_id}) : {retry_err}. "
                "Re-authentification OAuth manuelle requise."
            ) from retry_err

    # ──────────────────────────────────────────────────────────────────────────
    # CRUD
    # ──────────────────────────────────────────────────────────────────────────

    def _lire_token(self, workflow_id: int, mcp_type: str) -> McpToken:
        """Lit le McpToken en BDD. Lève McpTokenNotFoundError si absent."""
        token_db = (
            self.db.query(McpToken)
            .filter(
                McpToken.workflow_id == workflow_id,
                McpToken.mcp_type    == mcp_type,
            )
            .first()
        )
        if token_db is None:
            raise McpTokenNotFoundError(
                f"Aucun token MCP '{mcp_type}' en BDD pour "
                f"workflow_id={workflow_id}. "
                "L'utilisateur doit d'abord valider le flux OAuth."
            )
        return token_db

    def _sauvegarder_tokens(
        self,
        token_db: McpToken,
        nouveau_access: str,
        nouveau_refresh: str,
    ) -> None:
        """Met à jour access_token + refresh_token + updated_at en BDD."""
        token_db.access_token  = nouveau_access
        token_db.refresh_token = nouveau_refresh
        token_db.updated_at    = datetime.now(timezone.utc)
        self.db.commit()
        logger.info(
            f"[McpTokenService] Tokens persistés en BDD "
            f"(workflow_id={token_db.workflow_id}, mcp_type={token_db.mcp_type})."
        )

    def creer_ou_remplacer(
        self,
        workflow_id: int,
        mcp_type: str,
        token_public: str,
        access_token: str,
        refresh_token: str,
    ) -> McpToken:
        """
        Crée ou remplace le token MCP d'un workflow.
        Appelé par l'endpoint POST /executions/{workflow_id}/mcp-token.

        Args:
            workflow_id   (int): ID du workflow.
            mcp_type      (str): "github" | "gmail".
            token_public  (str): Client ID / clé publique OAuth.
            access_token  (str): Token court.
            refresh_token (str): Token long.

        Returns:
            McpToken: Enregistrement créé ou mis à jour.
        """
        existing = (
            self.db.query(McpToken)
            .filter(
                McpToken.workflow_id == workflow_id,
                McpToken.mcp_type    == mcp_type,
            )
            .first()
        )

        if existing:
            existing.token_public  = token_public
            existing.access_token  = access_token
            existing.refresh_token = refresh_token
            existing.updated_at    = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(existing)
            return existing

        token = McpToken(
            workflow_id=workflow_id,
            mcp_type=mcp_type,
            token_public=token_public,
            access_token=access_token,
            refresh_token=refresh_token,
        )
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    # ──────────────────────────────────────────────────────────────────────────
    # REFRESH OAUTH
    # ──────────────────────────────────────────────────────────────────────────

    def _rafraichir_token(self, token_db: McpToken) -> dict:
        """
        Appelle l'endpoint OAuth du provider pour obtenir de nouveaux tokens.

        Flux standard OAuth2 "refresh_token grant" :
          POST {REFRESH_URL}
          Body : grant_type=refresh_token & refresh_token=... & client_id=...

        Args:
            token_db (McpToken): Enregistrement contenant le refresh_token.

        Returns:
            dict: {"access_token": str, "refresh_token": str}

        Raises:
            McpTokenExpiredError: Si le refresh échoue (token révoqué/expiré).
        """
        mcp_type    = token_db.mcp_type
        refresh_url = REFRESH_URLS.get(mcp_type)

        if not refresh_url:
            raise McpTokenExpiredError(
                f"Aucune REFRESH_URL configurée pour '{mcp_type}'. "
                f"Ajouter MCP_{mcp_type.upper()}_REFRESH_URL dans .env."
            )

        logger.info(
            f"[McpTokenService] Appel OAuth refresh pour '{mcp_type}'..."
        )

        try:
            resp = requests.post(
                refresh_url,
                data={
                    "grant_type":    "refresh_token",
                    "refresh_token": token_db.refresh_token,
                    "client_id":     MCP_CLIENT_ID,
                    "client_secret": MCP_CLIENT_SECRET,
                },
                headers={"Accept": "application/json"},
                timeout=REQUEST_TIMEOUT,
            )
        except requests.exceptions.RequestException as e:
            raise McpTokenExpiredError(
                f"Erreur réseau lors du refresh OAuth '{mcp_type}' : {e}"
            ) from e

        if resp.status_code != 200:
            raise McpTokenExpiredError(
                f"Refresh OAuth '{mcp_type}' échoué "
                f"(HTTP {resp.status_code}) : {resp.text}. "
                "Re-authentification manuelle requise."
            )

        data = resp.json()
        if "access_token" not in data:
            raise McpTokenExpiredError(
                f"Réponse OAuth invalide pour '{mcp_type}' "
                f"(access_token absent) : {data}"
            )

        logger.info(
            f"[McpTokenService] Tokens OAuth rafraîchis pour '{mcp_type}'."
        )
        return {
            "access_token": data["access_token"],
            # Certains providers retournent un nouveau refresh, d'autres non
            "refresh_token": data.get("refresh_token", token_db.refresh_token),
        }