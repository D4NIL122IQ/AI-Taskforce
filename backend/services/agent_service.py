from backend.models.agent_model import AgentModel
from backend.appDatabase.init_db import init
>>>>>>> e2627ce3cc0265d58ec20149260718ceb174b63b:backend/services/agent_service.py
from sqlalchemy.orm import Session
from sqlalchemy import (insert, delete, update)
from pydantic import BaseModel

class AgentData(BaseModel):
    nom:str
    modele:str
    prompt:str
    max_token:int
    temperature:int
    user_id:int

class AgentService:
    """
        La classe logic pour la gestion du module Agent.
    """
    def __init__(self):
        self.all_agents = {}
        init()
        self.db : Session = next(get_db())

    def create_agent(self, nom, modele, prompt, max_token, temperature, user_id):
        try:
            agent=Agent(nom, modele, prompt, max_token, temperature)
            self.all_agents[agent.ID] = agent

            #enrisitrer dans la base de données
            stmt = insert(AgentModel).values(nom=agent.nom,
                                              modele=agent.modele,
                                              temperature=agent.temperature,
                                              max_token=agent.max_token,
                                              system_prompt=agent.prompt,
                                              user_id=user_id)
            self.db.execute(stmt)
            self.db.commit()

        
        except Exception as e:
            print(f"Erreur de creation d'agent :{e}") 
            return None
        
        return agent
    
    def update_agent(self, agent_id, nom=None, modele=None, prompt=None, max_token=None, temperature=None):
        try:
            agent = self.all_agents.get(agent_id)

            if not agent:
                raise ValueError("Agent introuvable")
            
            agent_id=agent.ID
            agent = Agent(nom, modele, prompt, max_token, temperature)
            self.all_agents[agent_id]= agent

            stmt = (
                update(AgentModel)
                .where(AgentModel.id == agent_id)
                .values(
                    nom=agent.nom,
                    modele=agent.modele,
                    system_prompt=agent.prompt,
                    max_token=agent.max_token,
                    temperature=agent.temperature
                )
            )

            self.db.execute(stmt)
            self.db.commit()

            return agent

        except Exception as e:
            print(f"Erreur update agent: {e}")
            return None
        
    def delete_agent(self, agent_id):
        """
            Supprime un agent
        """
        try:
            agent = self.all_agents.pop(agent_id, None)
            stmt = delete(AgentModel).where(AgentModel.id == agent_id)

            result = self.db.execute(stmt)
            self.db.commit()

            if result.rowcount == 0:
                raise ValueError("Agent introuvable en base")

            return True

        except Exception as e:
            print(f"Erreur suppression agent: {e}")
            return False

    @staticmethod
    def get_list_agent(self, id_user):
        return self.db.query(AgentModel).filter(AgentModel.user_id == id_user).all()
        
    @staticmethod
    def get_list_active_agents(db: Session):
        return db.query(AgentModel).filter(AgentModel.statut=="ACTIF").all()
        
    @staticmethod
    def get_agent(self, user_id:int, agent_id:int):
        return self.db.query(AgentModel).filter(AgentModel.id_agent==agent_id and AgentModel.id_user == user_id)
        
    def delete_user_agent(self, user_id, agent_id):
        agent=AgentService.get_agent(user_id, agent_id)
        self.db.delete(agent)
        self.db.commit()
            
