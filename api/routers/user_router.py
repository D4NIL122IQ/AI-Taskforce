from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.appDatabase.database import get_db
from backend.models.utilisateur_model import Utilisateur
from api.schemas.schema import UserData

router = APIRouter(prefix="/user", tags=["Users"])


# CREATE user
@router.post("/")
def create_user(data: UserData, db: Session = Depends(get_db)):
    try:
        new_user = Utilisateur(
            nom=data.nom,
            email=data.email,
            mot_de_passe=data.mot_de_passe
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"user_id": new_user.id_utilisateur}

    except Exception as e:
        return {"error": str(e)}


# LOGIN user (POST)
@router.post("/login")
def login_user(data: UserData, db: Session = Depends(get_db)):
    try:
        user = db.query(Utilisateur).filter(
            Utilisateur.email == data.email,
            Utilisateur.mot_de_passe == data.mot_de_passe
        ).first()

        if not user:
            return {"error": "-1", "message": "Email ou mot de passe incorrect"}

        return {
            "id": user.id_utilisateur,
            "nom": user.nom,
            "email": user.email
        }

    except Exception as e:
        return {"error": str(e)}


# GET user by id
@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(Utilisateur).filter(
            Utilisateur.id_utilisateur == user_id
        ).first()

        if not user:
            return {"error": "-1", "message": "Utilisateur non trouvé"}

        return {
            "id": user.id_utilisateur,
            "nom": user.nom,
            "email": user.email
        }

    except Exception as e:
        return {"error": str(e)}


# UPDATE user
@router.put("/{user_id}")
def update_user(user_id: int, data: UserData, db: Session = Depends(get_db)):
    try:
        user = db.query(Utilisateur).filter(
            Utilisateur.id_utilisateur == user_id
        ).first()

        if not user:
            return {"error": "Utilisateur non trouvé"}

        user.nom = data.nom
        user.email = data.email
        user.mot_de_passe = data.mot_de_passe

        db.commit()

        return {"message": "Utilisateur mis à jour"}

    except Exception as e:
        return {"error": str(e)}


# DELETE user
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(Utilisateur).filter(
            Utilisateur.id_utilisateur == user_id
        ).first()

        if not user:
            return {"error": "-1", "message": "Utilisateur non trouvé"}

        db.delete(user)
        db.commit()

        return {"message": "Utilisateur supprimé avec succès"}

    except Exception as e:
        return {"error": str(e)}