import pytest
from backend.services.users_service import UserService
from api.schemas.user_schema import UserData


@pytest.fixture
def user_service():
    """Instance du service utilisateur."""
    return UserService()


@pytest.fixture
def sample_user():
    """Données utilisateur de test."""
    return UserData(
        nom="Test User",
        email="test@example.com",
        mot_de_passe="password123"
    )


def test_create_user(user_service, sample_user):
    user_id = user_service.create_user(sample_user)

    assert user_id is not None


def test_get_user_by_id(user_service, sample_user):
    user_id = user_service.create_user(sample_user)

    user = user_service.get_user_by_id(user_id)

    assert user is not None
    assert user.email == sample_user.email


def test_login_user_success(user_service, sample_user):
    user_service.create_user(sample_user)

    user = user_service.login_user(
        sample_user.email,
        sample_user.mot_de_passe
    )

    assert user is not None


def test_login_user_fail(user_service, sample_user):
    user_service.create_user(sample_user)

    user = user_service.login_user(
        sample_user.email,
        "wrong_password"
    )

    assert user is None


def test_update_user(user_service, sample_user):
    user_id = user_service.create_user(sample_user)

    updated_data = UserData(
        nom="Updated",
        email="updated@example.com",
        mot_de_passe="newpass"
    )

    result = user_service.update_user(user_id, updated_data)

    updated_user = user_service.get_user_by_id(user_id)

    assert result is True
    assert updated_user.email == "updated@example.com"


def test_delete_user(user_service, sample_user):
    user_id = user_service.create_user(sample_user)

    result = user_service.delete_user(user_id)

    user = user_service.get_user_by_id(user_id)

    assert result is True
    assert user is None