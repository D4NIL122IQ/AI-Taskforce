from sqlalchemy.orm import Session
from sqlalchemy import insert, update, delete
from backend.models.utilisateur_model import Utilisateur as User
from api.schemas.user_schema import UserData
import bcrypt



class UserService:
    """
    Service responsable des opérations liées aux utilisateurs.
    Gère l'accès à la base de données et la logique métier associée.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, data: UserData) -> int:
        """
        Crée un utilisateur avec mot de passe hashé.
        Retourne l'identifiant du nouvel utilisateur.
        """
        try:
            password_hash = bcrypt.hashpw(
                data.mot_de_passe.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            stmt = insert(User).values(
                nom=data.nom,
                email=data.email,
                mot_de_passe=password_hash
            )

            result = self.db.execute(stmt)
            self.db.commit()

            return result.inserted_primary_key[0]

        except Exception as e:
            self.db.rollback()
            raise e


    def login_user(self, email: str, password: str):
        user = self.db.query(User).filter(User.email == email).first()
        """
        Vérifie les identifiants utilisateur.
        Retourne l'utilisateur si valide, sinon None.
        """
        if user and bcrypt.checkpw(
                password.encode("utf-8"),
                user.mot_de_passe.encode("utf-8") if isinstance(user.mot_de_passe, str) else user.mot_de_passe
        ):
            return user

        return None

    def get_user_by_id(self, user_id: int):
        """
        Récupère un utilisateur par son identifiant.
        """
        return self.db.query(User).filter(
            User.id_utilisateur == user_id
        ).first()

    def update_user(self, user_id: int, data: UserData) -> bool:
        """
        Met à jour les informations d’un utilisateur.
        """
        try:
            password_hash = bcrypt.hashpw(
                data.mot_de_passe.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            stmt = update(User).where(
                User.id_utilisateur == user_id
            ).values(
                nom=data.nom,
                email=data.email,
                mot_de_passe=password_hash
            )

            self.db.execute(stmt)
            self.db.commit()

            return True

        except Exception as e:
            self.db.rollback()
            raise e

    def delete_user(self, user_id: int) -> bool:
        """
        Supprime un utilisateur.
        """
        try:
            stmt = delete(User).where(
                User.id_utilisateur == user_id
            )

            self.db.execute(stmt)
            self.db.commit()

            return True

        except Exception as e:
            self.db.rollback()
            raise e