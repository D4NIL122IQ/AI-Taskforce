import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from back.models.message import Message


# ── Tests constructeur ─────────────────────────────────────────────────────

def test_creation_message_valide():
    msg = Message(contenu="Bonjour", type="user_input", expediteur="user")
    assert msg.contenu == "Bonjour"
    assert msg.type == "user_input"
    assert msg.expediteur == "user"
    assert msg.execution_id is None

def test_creation_agent_response():
    msg = Message(contenu="Voici mon analyse", type="agent_response", expediteur="Agent A")
    assert msg.type == "agent_response"
    assert msg.expediteur == "Agent A"

def test_creation_system():
    msg = Message(contenu="Workflow demarre", type="system", expediteur="system")
    assert msg.type == "system"


# ── Tests validations ──────────────────────────────────────────────────────

def test_contenu_vide_leve_erreur():
    with pytest.raises(ValueError, match="Contenu vide"):
        Message(contenu="", type="user_input", expediteur="user")

def test_type_inconnu_leve_erreur():
    with pytest.raises(ValueError, match="Type de message inconnu"):
        Message(contenu="Bonjour", type="mauvais_type", expediteur="user")


# ── Tests méthodes ─────────────────────────────────────────────────────────

def test_getContenu():
    msg = Message(contenu="Test contenu", type="user_input", expediteur="user")
    assert msg.getContenu() == "Test contenu"

def test_getDateCreation():
    msg = Message(contenu="Test", type="user_input", expediteur="user")
    assert msg.getDateCreation() is not None

def test_toDict():
    msg = Message(contenu="Test", type="user_input", expediteur="user")
    d = msg.toDict()
    assert d["contenu"] == "Test"
    assert d["type"] == "user_input"
    assert d["expediteur"] == "user"
    assert d["execution_id"] is None