# tests/mcp_token_test.py
import pytest
from unittest.mock import MagicMock, patch
from backend.services.mcp_token_service import (
    McpTokenService, McpTokenNotFoundError, McpTokenExpiredError
)


def make_db(token_db=None):
    """Crée une session SQLAlchemy mockée."""
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = token_db
    return db


def make_token_db():
    """Crée un faux McpToken en mémoire."""
    t = MagicMock()
    t.token_public  = "client_id_123"
    t.access_token  = "access_token_valide"
    t.refresh_token = "refresh_token_valide"
    t.mcp_type      = "github"
    t.workflow_id   = 1
    return t


def make_agent():
    """Crée un faux Agent."""
    agent = MagicMock()
    agent.nom = "testeur"
    return agent


# ── Test 1 : token absent en BDD ──────────────────────────────────────────────
def test_token_absent_leve_erreur():
    db  = make_db(token_db=None)  # ← rien en BDD
    svc = McpTokenService(db)
    agent = make_agent()

    with pytest.raises(McpTokenNotFoundError):
        svc.connecter_agent_mcp(agent, workflow_id=1, mcp_type="github")

    print("✅ McpTokenNotFoundError levée correctement")


# ── Test 2 : token valide → connexion directe ─────────────────────────────────
def test_connexion_directe_succes():
    token_db = make_token_db()
    db       = make_db(token_db)
    svc      = McpTokenService(db)
    agent    = make_agent()

    # connecter_mcp ne lève pas d'erreur → succès direct
    agent.connecter_mcp.return_value = MagicMock()

    svc.connecter_agent_mcp(agent, workflow_id=1, mcp_type="github")

    agent.connecter_mcp.assert_called_once_with(
        token_public="client_id_123",
        token_tempo="access_token_valide",
        mcp="github",
    )
    print("✅ Connexion directe avec token valide OK")


# ── Test 3 : token expiré → refresh → reconnexion ─────────────────────────────
def test_refresh_automatique_apres_401():
    token_db = make_token_db()
    db       = make_db(token_db)
    svc      = McpTokenService(db)
    agent    = make_agent()

    # Premier appel lève une erreur 401, second réussit
    agent.connecter_mcp.side_effect = [
        Exception("401 Unauthorized"),
        None,  # ← retry réussi
    ]

    nouveaux_tokens = {
        "access_token": "nouveau_access",
        "refresh_token": "nouveau_refresh",
    }

    with patch.object(svc, "_rafraichir_token", return_value=nouveaux_tokens):
        with patch.object(svc, "_sauvegarder_tokens") as mock_save:
            svc.connecter_agent_mcp(agent, workflow_id=1, mcp_type="github")

            # Vérifier que la BDD a été mise à jour
            mock_save.assert_called_once_with(
                token_db=token_db,
                nouveau_access="nouveau_access",
                nouveau_refresh="nouveau_refresh",
            )

    # Vérifier que l'agent a été reconnecté avec le nouveau token
    assert agent.connecter_mcp.call_count == 2
    second_call = agent.connecter_mcp.call_args_list[1]
    assert second_call[1]["token_tempo"] == "nouveau_access"
    print("✅ Refresh automatique + mise à jour BDD OK")


# ── Test 4 : creer_ou_remplacer ───────────────────────────────────────────────
def test_creer_token():
    db = make_db(token_db=None)  # rien en BDD → création
    svc = McpTokenService(db)

    svc.creer_ou_remplacer(
        workflow_id=1,
        mcp_type="github",
        token_public="pub",
        access_token="acc",
        refresh_token="ref",
    )

    db.add.assert_called_once()
    db.commit.assert_called()
    print("✅ creer_ou_remplacer (création) OK")