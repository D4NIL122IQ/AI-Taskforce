from fastapi import APIRouter
from backend.services.users_service import UserService, UserData

router = APIRouter()
service = UserService()

@router.post("/user/creation")
def create_user(data:UserData):
    user_id = service.create_user(**data)
    if user_id:
        return {"user_id": user_id}
    else :
        return {"error": "Failed to create user"}

@router.get("/user/login")
def login_user(email:str, password:str):
    user = service.get_user_by_email_and_password(email, password)
    if user:
        return UserData(nom=user.nom, email=user.email, mot_de_passe=user.mot_de_passe)
    else:
        return {"error": "-1", "message": "Email ou mot de passe incorrect"}
    
@router.get("/user/{user_id}")
def get_user(user_id: int):
    try:
        user = service.get_user_by_id(user_id)
        if user:
            return user
        else:
            return {"error": "-1", "message": "Utilisateur non trouvé"}
        
    except Exception as e:
        print("ERREUR:", e)
        return {"error": str(e)}
    
@router.put("/user/{user_id}")
def save_user(user_id: int, data: UserData):
    try:
        result = service.update_user(user_id, **data.dict())
        return result
    except Exception as e:
        print("ERREUR:", e)
        return {"error": str(e)}

@router.delete("/user/{user_id}")
def delete_user(user_id: int):
    try:
        result = service.delete_user(user_id)
        if result:
            return {"message": "Utilisateur supprimé avec succès"}
        else:
            return {"error": "-1", "message": "Utilisateur non trouvé"}
    except Exception as e:
        print("ERREUR:", e)
        return {"error": str(e)} 

@router.post("/user/login")
def login_user(email:str, password:str):
    user = service.get_user_by_email_and_password(email, password)
    if user:
        return UserData(nom=user.nom, email=user.email, mot_de_passe=user.mot_de_passe) 
    else:
        return {"error": "-1", "message": "Email ou mot de passe incorrect"}
