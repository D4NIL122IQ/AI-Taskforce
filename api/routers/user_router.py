from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from api.schemas.user_schema import UserData, UserLogin
from backend.services.users_service import UserService
from backend.appDatabase.database import get_db

router = APIRouter(prefix="/user", tags=["Users"])


@router.post("/")
def create_user(data: UserData, db: Session = Depends(get_db)):
    try:
        svc = UserService(db)
        user_id = svc.create_user(data)
        return {"user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
def login_user(data: UserLogin, db: Session = Depends(get_db)):
    try:
        svc = UserService(db)
        user = svc.login_user(data.email, data.mot_de_passe)
        if not user:
            raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
        return {"user_id": user.id_utilisateur, "nom": user.nom, "email": user.email}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        svc = UserService(db)
        user = svc.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        return {"user_id": user.id_utilisateur, "nom": user.nom, "email": user.email}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}")
def update_user(user_id: int, data: UserData, db: Session = Depends(get_db)):
    try:
        svc = UserService(db)
        success = svc.update_user(user_id, data)
        if not success:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        return {"message": "Utilisateur mis à jour"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        svc = UserService(db)
        success = svc.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        return {"message": "Utilisateur supprimé avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))