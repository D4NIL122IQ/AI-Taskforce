from backend.models.users_model import User
from backend.appDatabase.init_db import init
from backend.appDatabase.database import get_db
from sqlalchemy.orm import Session
import bcrypt
from sqlalchemy import (insert, delete, update)
from pydantic import BaseModel

class UserData(BaseModel):
    nom:str
    email:str
    mot_de_passe:str

class UserService:
    """
        la classe de service pour la requette des operations utilisateurs  
    """

    def __init__(self):
        self.all_users = []
        init()
        self.db : Session = next(get_db())
    
    def create_user(self, nom, mail, password):
        password_crypt = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            stmt = insert(User).values(nom=nom, email=mail, mot_de_passe=password_crypt)
            result = self.db.execute(stmt)
            self.db.commit()
            return result.inserted_primary_key[0]  # Retourne l'ID de l'utilisateur créé
        except Exception as e:
            self.db.rollback()
            raise e
        return {"message": "Utilisateur créé avec succès"}
    
    def get_user_by_email(self, email):
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_email_and_password(self, email, password):
        user = self.get_user_by_email(email)
        if user and bcrypt.checkpw(password.encode('utf-8'), user.mot_de_passe):
            return UserData(ID=user.user_id, nom=user.nom, email=user.email, mot_de_passe=user.mot_de_passe)
        return None

    def get_user_by_id(self, user_id):
        self.db.query(User).filter(User.user_id == user_id).first()
    
    def delete_user(self, user_id):
        """Supprimer un utilisateur de la base de données."""
        try:
            stmt = delete(User).where(User.user_id == user_id)
            self.db.execute(stmt)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        return True

    def update_user(self, user_id, nom=None, email=None, mot_de_passe=None):
        """Mettre à jour les informations d'un utilisateur."""
        try:
            stmt = update(User).where(User.user_id == user_id)
            if nom:
                stmt = stmt.values(nom=nom)
            if email:
                stmt = stmt.values(email=email)
            if mot_de_passe:
                password_crypt = bcrypt.hashpw(mot_de_passe.encode('utf-8'), bcrypt.gensalt())
                stmt = stmt.values(mot_de_passe=password_crypt)
            self.db.execute(stmt)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        return {"bool": "1"}   

    def get_all_users(self):
        """Récupérer tous les utilisateurs de la base de données."""
        return self.db.query(User).all().to_list()
    
    