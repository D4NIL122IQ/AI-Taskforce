# backend/services/agent_service.py

from sqlalchemy.orm import Session
from backend.models.agent_model import Agent
from api.schemas.agent_schema import AgentBase
from typing import List, Optional


class AgentService:
    """
    Service de gestion des agents.
    Fournit les opérations CRUD via ORM SQLAlchemy.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_agents_by_user(self, user_id: int) -> List[Agent]:
        """
        Retourne la liste des agents d’un utilisateur.
        """
        return self.db.query(Agent).filter(
            Agent.utilisateur_id == user_id
        ).order_by(Agent.date_creation.desc()).all()

    def create_agent(self, data: AgentBase) -> int:
        """
        Crée un agent et retourne son identifiant.
        """
        try:
            agent = Agent(
                nom=data.nom,
                modele=data.modele,
                system_prompt=data.system_prompt,
                max_tokens=data.max_tokens,
                temperature=data.temperature,
                web_search=1 if data.web_search else 0,
                utilisateur_id=data.utilisateur_id
            )

            self.db.add(agent)
            self.db.commit()
            self.db.refresh(agent)

            return agent.id_agent

        except Exception as e:
            self.db.rollback()
            raise e

    def update_agent(self, agent_id: int, data: AgentBase) -> bool:
        """
        Met à jour un agent existant.
        Retourne True si succès, False sinon.
        """
        try:
            agent: Optional[Agent] = self.db.query(Agent).filter(
                Agent.id_agent == agent_id
            ).first()

            if not agent:
                return False

            agent.nom = data.nom
            agent.modele = data.modele
            agent.system_prompt = data.system_prompt
            agent.max_tokens = data.max_tokens
            agent.temperature = data.temperature
            agent.web_search = 1 if data.web_search else 0

            self.db.commit()

            return True

        except Exception as e:
            self.db.rollback()
            raise e

    def delete_agent(self, agent_id: int) -> bool:
        """
        Supprime un agent.
        Retourne True si supprimé, False sinon.
        """
        try:
            agent: Optional[Agent] = self.db.query(Agent).filter(
                Agent.id_agent == agent_id
            ).first()

            if not agent:
                return False

            self.db.delete(agent)
            self.db.commit()

            return True

        except Exception as e:
            self.db.rollback()
            raise e
