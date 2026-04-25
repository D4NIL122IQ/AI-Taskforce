# api/routers/agent_router.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.appDatabase.database import get_db
from api.schemas.agent_schema import AgentBase, AgentCreate, AgentUpdate
from backend.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("/{user_id}")
def get_agents(user_id: str, db: Session = Depends(get_db)):
    """
    Retourne la liste des agents appartenant à un utilisateur.

    - **user_id** : identifiant de l'utilisateur
    - **Retourne** : liste de dicts contenant les champs de chaque agent
    - **500** : erreur serveur inattendue
    """
    try:
        svc = AgentService(db)
        agents = svc.get_agents_by_user(user_id)
        return [
            {
                "id": a.id_agent,
                "nom": a.nom,
                "role": a.role,
                "modele": a.modele,
                "system_prompt": a.system_prompt,
                "max_tokens": a.max_tokens,
                "temperature": a.temperature,
                "statut": a.statut,
                "web_search": bool(a.web_search),
                "generate_document": bool(a.generate_document),
                "mcp_type": a.mcp_type,
            }
            for a in agents
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
def create_agent(data: AgentBase, db: Session = Depends(get_db)):
    """
    Crée un nouvel agent en base de données.

    - **data** : champs de l'agent (voir AgentBase)
    - **Retourne** : l'identifiant de l'agent créé
    - **500** : erreur serveur inattendue
    """
    try:
        svc = AgentService(db)
        agent_id = svc.create_agent(data)
        return {"agent_id": agent_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{agent_id}")
def update_agent(agent_id: int, data: AgentBase, db: Session = Depends(get_db)):
    """
    Met à jour un agent existant.

    - **agent_id** : identifiant de l'agent à modifier
    - **data** : nouvelles valeurs des champs (voir AgentBase)
    - **Retourne** : message de confirmation
    - **404** : agent introuvable
    - **500** : erreur serveur inattendue
    """
    try:
        svc = AgentService(db)
        success = svc.update_agent(agent_id, data)
        if not success:
            raise HTTPException(status_code=404, detail="Agent non trouvé")
        return {"message": "Agent mis à jour"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{agent_id}")
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    """
    Supprime un agent de la base de données.

    - **agent_id** : identifiant de l'agent à supprimer
    - **Retourne** : message de confirmation
    - **404** : agent introuvable
    - **500** : erreur serveur inattendue
    """
    try:
        svc = AgentService(db)
        success = svc.delete_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent non trouvé")
        return {"message": "Agent supprimé avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))