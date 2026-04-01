from fastapi import APIRouter
from back.services.agent_service import AgentService, AgentData

router = APIRouter()
service = AgentService()

@router.get("/agent/{user_id}")
def get_agents(user_id: int):
    try:
        return service.get_list_agent(service, user_id)
    except Exception as e:
        print("ERREUR:", e)
        return {"error": str(e)}



@router.get("/agent/creation/{user_id}")
def create_agent(data:AgentData, user_id:int):
    agent = service.create_agent(**data, user_id= user_id)
    return agent