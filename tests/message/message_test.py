import pytest
from datetime import datetime
from back.logic.Message import Message, MessageType


class FakeAgent:
    def __init__(self, nom):
        self.nom = nom


# test de création valide
def test_message_creation_valide():
    sender = FakeAgent("Agent1")
    msg = Message(sender, "Hello", MessageType.USER, {})

    assert msg.content == "Hello"
    assert msg.sender.nom == "Agent1"
    assert msg.type == MessageType.USER
    assert isinstance(msg.date, datetime)
    assert msg.metadata == {}


# test de contenu vide
def test_message_contenu_vide():
    sender = FakeAgent("Agent1")

    with pytest.raises(ValueError):
        Message(sender, "", MessageType.USER, {})


# test de Sender invalide
def test_sender_invalide():
    with pytest.raises(ValueError):
        Message(None, "Hello", MessageType.USER, {})


# test de Type invalide
def test_type_invalide():
    sender = FakeAgent("Agent1")

    with pytest.raises(ValueError):
        Message(sender, "Hello", "USER", {})


# test de conversion en dictionnaire
def test_to_dict():
    sender = FakeAgent("Agent1")
    msg = Message(sender, "Hello", MessageType.USER, {"key": "value"})

    data = msg.to_dict()

    assert data["sender"] == "Agent1"
    assert data["content"] == "Hello"
    assert data["type"] == "user"
    assert "date" in data
    assert data["metadata"] == {"key": "value"}


#  test de type user 
def test_is_user_message():
    sender = FakeAgent("Agent1")
    msg = Message(sender, "Hello", MessageType.USER, {})

    assert msg.is_user_message()
    assert not msg.is_agent_message()


# test de  type agent
def test_is_agent_message():
    sender = FakeAgent("Agent1")
    msg = Message(sender, "Hello", MessageType.AGENT, {})

    assert msg.is_agent_message()
    assert not msg.is_user_message()


# test des messages de meme contenu
def test_same_message():
    sender = FakeAgent("Agent1")

    msg1 = Message(sender, "Hello", MessageType.USER, {})
    msg2 = Message(sender, "Hello", MessageType.USER, {})

    assert msg1.same_message(msg2)


# test same_message différent
def test_same_message_false():
    sender = FakeAgent("Agent1")

    msg1 = Message(sender, "Hello", MessageType.USER, {})
    msg2 = Message(sender, "Hi", MessageType.USER, {})

    assert not msg1.same_message(msg2)


# test égalité d'egalité d'instance
def test_message_equality():
    sender = FakeAgent("Agent1")

    msg1 = Message(sender, "Hello", MessageType.USER, {})
    msg2 = msg1

    assert msg1 == msg2


# test égalité différente
def test_message_not_equal():
    sender = FakeAgent("Agent1")

    msg1 = Message(sender, "Hello", MessageType.USER, {})
    msg2 = Message(sender, "Hello", MessageType.USER, {})

    assert msg1 != msg2