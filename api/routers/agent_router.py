# api/routers/agent_router.py

from fastapi import APIRouter
from api.schemas.agent_schema import AgentBase, AgentCreate, AgentUpdate
from backend.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["Agents"])

service = AgentService()


@router.get("/{user_id}")
def get_agents(user_id: int):
    try:
        agents = service.get_agents_by_user(user_id)

        return [
            {
                "id": a.id_agent,
                "nom": a.nom,
                "modele": a.modele,
                "prompt": a.system_prompt,
                "max_token": a.max_tokens,
                "temperature": a.temperature,
                "statut": a.statut
            }
            for a in agents
        ]

    except Exception as e:
        return {"error": str(e)}


@router.post("/")
def create_agent(data: AgentBase):
    try:
        agent_id = service.create_agent(data)
        return {"agent_id": agent_id}
    except Exception as e:
        return {"error": str(e)}


@router.put("/{agent_id}")
def update_agent(agent_id: int, data: AgentBase):
    try:
        success = service.update_agent(agent_id, data)

        if not success:
            return {"error": "Agent non trouvé"}

        return {"message": "Agent mis à jour"}

    except Exception as e:
        return {"error": str(e)}


@router.delete("/{agent_id}")
def delete_agent(agent_id: int):
    try:
        success = service.delete_agent(agent_id)

        if not success:
            return {"error": "-1", "message": "Agent non trouvé"}

        return {"message": "Agent supprimé avec succès"}

    except Exception as e:
        return {"error": str(e)}