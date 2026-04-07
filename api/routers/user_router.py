# api/routers/user_router.py

from fastapi import APIRouter,HTTPException
from api.schemas.user_schema import UserData, UserLogin
from backend.services.users_service import UserService

router = APIRouter(prefix="/user", tags=["Users"])

service = UserService()


@router.post("/")
def create_user(data: UserData):
    try:
        user_id = service.create_user(data)
        return {"user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
def login_user(data: UserLogin):
    try:
        user = service.login_user(data.email, data.mot_de_passe)

        if not user:
            raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
        return {
            "user_id": user.id_utilisateur,
            "nom": user.nom,
            "email": user.email
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}")
def get_user(user_id: int):
    try:
        user = service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        return {
            "user_id": user.id_utilisateur,
            "nom": user.nom,
            "email": user.email
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}")
def update_user(user_id: int, data: UserData):
    try:
        success = service.update_user(user_id, data)

        if not success:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")  # ← corriger
        return {"message": "Utilisateur mis à jour"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.delete("/{user_id}")
def delete_user(user_id: int):
    try:
        success = service.delete_user(user_id)

        if not success:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")  # ← corriger
        return {"message": "Utilisateur supprimé avec succès"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))