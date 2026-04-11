# api/routers/agent_router.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.appDatabase.database import get_db
from api.schemas.agent_schema import AgentBase, AgentCreate, AgentUpdate
from backend.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.get("/{user_id}")
def get_agents(user_id: str, db: Session = Depends(get_db)):
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
            }
            for a in agents
        ]


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
def create_agent(data: AgentBase, db: Session = Depends(get_db)):
    try:
        svc = AgentService(db)
        agent_id = svc.create_agent(data)
        return {"agent_id": agent_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{agent_id}")
def update_agent(agent_id: int, data: AgentBase, db: Session = Depends(get_db)):
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