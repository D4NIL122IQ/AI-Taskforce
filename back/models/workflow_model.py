from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from back.appDatabase.database import Base


class Workflow(Base):
    __tablename__ = "workflow"

    id_workflow         = Column(Integer,     primary_key=True, autoincrement=True)
    nom                 = Column(String(100), nullable=False)
    donnees_graphe_json = Column(JSON,        nullable=True)
    superviseur_id      = Column(Integer,     ForeignKey("agent.id_agent"), nullable=True)
    date_creation       = Column(DateTime,    default=lambda: datetime.now(timezone.utc))

    superviseur = relationship("Agent", foreign_keys=[superviseur_id])
    etapes      = relationship("Etape",     back_populates="workflow",
                               cascade="all, delete-orphan")
    executions  = relationship("Execution", back_populates="workflow",
                               cascade="all, delete-orphan")

    def __init__(self, nom: str,
                 donnees_graphe_json: dict = None,
                 date_creation: datetime = None):
        if not nom or len(nom) > 100:
            raise ValueError("Nom invalide : doit être non vide et <= 100 caractères")

        self.nom                 = nom
        self.donnees_graphe_json = donnees_graphe_json or {
            "superviseur": None,
            "agents_specialises": []
        }
        self.date_creation = date_creation or datetime.now(timezone.utc)

    def validateWorkflow(self, nodes: list, edges: list) -> bool:
        agent_nodes = [n for n in nodes if n.get("type") == "agent"]
        if len(agent_nodes) == 0:
            raise ValueError("Au moins un agent spécialisé requis")

        superviseur_nodes = [n for n in nodes if n.get("type") == "supervisor"]
        if len(superviseur_nodes) != 1:
            raise ValueError("Exactement un superviseur requis")

        agent_ids = {n["id"] for n in agent_nodes}
        for edge in edges:
            if edge["source"] in agent_ids and edge["target"] in agent_ids:
                raise ValueError(
                    f"Connexion agent->agent interdite : "
                    f"{edge['source']} -> {edge['target']}"
                )

        superviseur_id = superviseur_nodes[0]["id"]
        for edge in edges:
            if edge["source"] != superviseur_id and edge["target"] != superviseur_id:
                raise ValueError(
                    f"Arete hors structure etoile detectee : "
                    f"{edge['source']} -> {edge['target']}"
                )

        return True

    def ajouterAgentSpecialise(self, agent_config: dict) -> None:
        agents = self.donnees_graphe_json.get("agents_specialises", [])
        ids_existants = {a["id"] for a in agents}
        if agent_config.get("id") in ids_existants:
            raise ValueError("Agent déjà présent dans le workflow")
        agents.append(agent_config)
        self.donnees_graphe_json["agents_specialises"] = agents

    def retirerAgentSpecialise(self, agent_id: str) -> None:
        superviseur = self.donnees_graphe_json.get("superviseur") or {}
        if superviseur.get("id") == agent_id:
            raise ValueError("Impossible de retirer le superviseur")
        agents = self.donnees_graphe_json.get("agents_specialises", [])
        avant  = len(agents)
        agents = [a for a in agents if a["id"] != agent_id]
        if len(agents) == avant:
            raise ValueError("Agent absent du workflow")
        self.donnees_graphe_json["agents_specialises"] = agents

    def handleSupervisorDesignate(self, superviseur_config: dict) -> None:
        if not superviseur_config.get("id"):
            raise ValueError("Config superviseur invalide : id manquant")
        self.donnees_graphe_json["superviseur"] = superviseur_config

    def sauvegarderWorkflow(self) -> None:
        superviseur = self.donnees_graphe_json.get("superviseur")
        agents      = self.donnees_graphe_json.get("agents_specialises", [])
        nodes = []
        if superviseur:
            nodes.append({"id": superviseur["id"], "type": "supervisor"})
        for a in agents:
            nodes.append({"id": a["id"], "type": "agent"})
        edges = []
        if superviseur:
            for a in agents:
                edges.append({"source": superviseur["id"], "target": a["id"]})
                edges.append({"source": a["id"],           "target": superviseur["id"]})
        self.validateWorkflow(nodes, edges)

    def visualiserWorkflow(self) -> dict:
        return {
            "superviseur":        self.donnees_graphe_json.get("superviseur"),
            "agents_specialises": self.donnees_graphe_json.get("agents_specialises", [])
        }

    def toDict(self) -> dict:
        return {
            "id_workflow":         self.id_workflow,
            "nom":                 self.nom,
            "donnees_graphe_json": self.donnees_graphe_json,
            "superviseur_id":      self.superviseur_id,
            "date_creation":       str(self.date_creation),
        }

    def __repr__(self):
        return f"<Workflow id={self.id_workflow} nom={self.nom}>"