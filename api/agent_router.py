from fastapi import APIRouter
from backend.services.agent_service import AgentService, AgentData

router = APIRouter()
service = AgentService()

@router.get("/agent/{user_id}")
def get_agents(user_id: int):
    try:
        return service.get_list_agent(service, user_id)
    except Exception as e:
        print("ERREUR:", e)
        return {"error": str(e)}



@router.post("/agent/creation/{user_id}")
def create_agent(data:AgentData, user_id:int):
    id = service.create_agent(**data, user_id= user_id)
    if id:
        return {"agent_id": id}
    else :
        return {"error": "Failed to create agent"}

@router.put("/agent/{agent_id}")
def update_agent(agent_id: int, data: AgentData):
    try:
        result = service.update_agent(agent_id, **data)
        return result
    except Exception as e:
        print("ERREUR:", e)
        return {"error": str(e)}
    
@router.delete("/agent/{agent_id}")
def delete_agent(agent_id: int):
    try:
        result = service.delete_agent(agent_id)
        if result:
            return {"message": "Agent supprimé avec succès"}
        else:
            return {"error": "-1", "message": "Agent non trouvé"}
    except Exception as e:
        print("ERREUR:", e)
        return {"error": str(e)}