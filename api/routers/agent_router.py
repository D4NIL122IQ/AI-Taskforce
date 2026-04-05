from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.appDatabase.database import get_db
from backend.models.agent_model import Agent
from api.schemas.schema import AgentData

router = APIRouter(prefix="/agents", tags=["Agents"])


# GET agents par user
@router.get("/{user_id}")
def get_agents(user_id: int, db: Session = Depends(get_db)):
    try:
        agents = db.query(Agent).filter(Agent.utilisateur_id == user_id).all()

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


# CREATE agent
@router.post("/")
def create_agent(data: AgentData, db: Session = Depends(get_db)):
    try:
        new_agent = Agent(
            nom=data.nom,
            modele=data.modele,
            prompt=data.prompt,
            max_token=data.max_token,
            temperature=data.temperature,
            user_id=data.user_id
        )

        db.add(new_agent)
        db.commit()
        db.refresh(new_agent)

        return {"agent_id": new_agent.id_agent}

    except Exception as e:
        return {"error": str(e)}


# UPDATE agent
@router.put("/{agent_id}")
def update_agent(agent_id: int, data: AgentData, db: Session = Depends(get_db)):
    try:
        agent = db.query(Agent).filter(Agent.id_agent == agent_id).first()

        if not agent:
            return {"error": "Agent non trouvé"}

        agent.nom = data.nom
        agent.modele = data.modele
        agent.prompt = data.prompt
        agent.max_token = data.max_token
        agent.temperature = data.temperature

        db.commit()

        return {"message": "Agent mis à jour"}

    except Exception as e:
        return {"error": str(e)}


# DELETE agent
@router.delete("/{agent_id}")
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    try:
        agent = db.query(Agent).filter(Agent.id_agent == agent_id).first()

        if not agent:
            return {"error": "-1", "message": "Agent non trouvé"}

        db.delete(agent)
        db.commit()

        return {"message": "Agent supprimé avec succès"}

    except Exception as e:
        return {"error": str(e)}