from sqlalchemy import Column, Integer, String, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from back.database import Base

STATUTS_VALIDES = {"EN_ATTENTE", "EN_COURS", "TERMINE", "ERREUR"}

# Machine à états finie (conception v2 §3.5.3)
TRANSITIONS_VALIDES = {
    "EN_ATTENTE": ["EN_COURS"],
    "EN_COURS":   ["TERMINE", "ERREUR"],
    "TERMINE":    [],               # état terminal
    "ERREUR":     ["EN_ATTENTE"]    # retry possible
}


class Etape(Base):
    __tablename__ = "etape"

    id_etape          = Column(Integer,     primary_key=True, autoincrement=True)
    ordre_execution   = Column(Integer,     nullable=False)
    description_tache = Column(Text,        nullable=True)
    statut_etape      = Column(String(20),  nullable=False, default="EN_ATTENTE")
    agent_id          = Column(Integer,     ForeignKey("agent.id_agent"),    nullable=True)
    workflow_id       = Column(Integer,     ForeignKey("workflow.id_workflow"), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "ordre_execution >= 1",
            name="ck_etape_ordre"
        ),
        CheckConstraint(
            "statut_etape IN ('EN_ATTENTE','EN_COURS','TERMINE','ERREUR')",
            name="ck_etape_statut"
        ),
    )

    agent    = relationship("Agent",    back_populates="etapes")
    workflow = relationship("Workflow", back_populates="etapes")

    def __init__(self, ordre_execution: int, workflow_id: int,
                 description_tache: str = None, agent_id: int = None):
        if ordre_execution < 1:
            raise ValueError("L'ordre doit être >= 1")

        self.ordre_execution   = ordre_execution
        self.workflow_id       = workflow_id
        self.description_tache = description_tache
        self.agent_id          = agent_id
        self.statut_etape      = "EN_ATTENTE"

    # ------------------------------------------------------------------
    # Méthodes métier
    # ------------------------------------------------------------------

    def definirEtape(self, description: str, agent_id: int) -> None:
        """Assigne une description et un agent à l'étape."""
        if not description:
            raise ValueError("Description de tâche vide")
        self.description_tache = description
        self.agent_id          = agent_id

    def modifierOrdre(self, nouvel_ordre: int) -> None:
        """Modifie la position de l'étape dans le workflow."""
        if nouvel_ordre < 1:
            raise ValueError("L'ordre doit être >= 1")
        self.ordre_execution = nouvel_ordre

    def changerStatut(self, nouveau_statut: str) -> None:
        """
        Applique une transition d'état selon la machine à états finie.
        Transitions valides :
          EN_ATTENTE → EN_COURS
          EN_COURS   → TERMINE | ERREUR
          ERREUR     → EN_ATTENTE  (retry)
          TERMINE    → (terminal)
        """
        if nouveau_statut not in STATUTS_VALIDES:
            raise ValueError(f"Statut inconnu : {nouveau_statut}")
        if nouveau_statut not in TRANSITIONS_VALIDES[self.statut_etape]:
            raise ValueError(
                f"Transition invalide : {self.statut_etape} → {nouveau_statut}"
            )
        self.statut_etape = nouveau_statut

    def toDict(self) -> dict:
        return {
            "id_etape":          self.id_etape,
            "ordre_execution":   self.ordre_execution,
            "description_tache": self.description_tache,
            "statut_etape":      self.statut_etape,
            "agent_id":          self.agent_id,
            "workflow_id":       self.workflow_id,
        }

    def __repr__(self):
        return (f"<Etape ordre={self.ordre_execution} "
                f"statut={self.statut_etape} agent_id={self.agent_id}>")