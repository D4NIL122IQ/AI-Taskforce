import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from back.models.message import Message

# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def message_valide():
    return Message(
        contenu="Bonjour",
        type="user_input",
        expediteur="alice"
    )

# ──────────────────────────────────────────────
# __init__ — cas valides
# ──────────────────────────────────────────────

class TestMessageInit:

    def test_creation_minimale(self, message_valide):
        assert message_valide.contenu == "Bonjour"
        assert message_valide.type == "user_input"
        assert message_valide.expediteur == "alice"
        assert message_valide.execution_id is None

    def test_date_creation_auto(self, message_valide):
        assert isinstance(message_valide.date_creation, datetime)

    def test_date_creation_explicite(self):
        date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        msg = Message(contenu="Test", type="system", expediteur="sys", date_creation=date)
        assert msg.date_creation == date

    @pytest.mark.parametrize("type_valide", ["user_input", "agent_response", "system"])
    def test_types_valides(self, type_valide):
        msg = Message(contenu="ok", type=type_valide, expediteur="bot")
        assert msg.type == type_valide

# ──────────────────────────────────────────────
# __init__ — cas invalides
# ──────────────────────────────────────────────

class TestMessageInitErreurs:

    def test_contenu_vide(self):
        with pytest.raises(ValueError, match="Contenu vide"):
            Message(contenu="", type="user_input", expediteur="alice")

    def test_contenu_none(self):
        with pytest.raises(ValueError):
            Message(contenu=None, type="user_input", expediteur="alice")

    @pytest.mark.parametrize("type_invalide", ["admin", "bot", "", "USER_INPUT", "Agent_Response"])
    def test_type_invalide(self, type_invalide):
        with pytest.raises(ValueError, match="Type de message inconnu"):
            Message(contenu="Test", type=type_invalide, expediteur="alice")

# ──────────────────────────────────────────────
# Getters
# ──────────────────────────────────────────────

class TestMessageGetters:

    def test_get_contenu(self, message_valide):
        assert message_valide.getContenu() == "Bonjour"

    def test_get_date_creation(self, message_valide):
        assert isinstance(message_valide.getDateCreation(), datetime)

# ──────────────────────────────────────────────
# toDict
# ──────────────────────────────────────────────

class TestMessageToDict:

    def test_cles_presentes(self, message_valide):
        d = message_valide.toDict()
        assert set(d.keys()) == {"id", "contenu", "date_creation", "type", "expediteur", "execution_id"}

    def test_valeurs_correctes(self, message_valide):
        d = message_valide.toDict()
        assert d["contenu"] == "Bonjour"
        assert d["type"] == "user_input"
        assert d["expediteur"] == "alice"
        assert d["execution_id"] is None

    def test_date_creation_est_string(self, message_valide):
        d = message_valide.toDict()
        assert isinstance(d["date_creation"], str)

# ──────────────────────────────────────────────
# __repr__
# ──────────────────────────────────────────────

class TestMessageRepr:

    def test_repr(self, message_valide):
        assert repr(message_valide) == "<Message [user_input] de alice>"

# ──────────────────────────────────────────────
# Relation execution
# ──────────────────────────────────────────────

class TestMessageRelation:

    def test_execution_id_assignable(self, message_valide):
        message_valide.execution_id = 42
        assert message_valide.execution_id == 42

    def test_execution_mock(self, message_valide):
        mock_exec = MagicMock()
        mock_exec.id_execution = 99
        message_valide.execution = mock_exec
        assert message_valide.execution.id_execution == 99