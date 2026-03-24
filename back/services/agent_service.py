from back.models.agent_model import agents
from back.appDatabase.init_db import init
from sqlalchemy.orm import Session

class AgentService:

    @staticmethod
    def get_list_agent(db:Session, id_user):
        return db.query(agents).filter(agents.id_user == id_user).all()
    
    @staticmethod
    def get_list_active_agents(db: Session):
        return db.query(agents).filter(agents.statut=="ACTIF").all()
    
    @staticmethod
    def get_agent(db:Session, user_id:int, agent_id:int):
        
        return db.query(agents).filter(agents.id_agent==agent_id and agents.id_user == user_id)

    
    @staticmethod
    def delete_user_agent(db:Session, user_id, agent_id):
        agent=AgentService.get_agent(db, user_id, agent_id)
        db.delete(agent)
        db.commit()
        
