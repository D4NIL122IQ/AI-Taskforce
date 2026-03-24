from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
from back.database import Base

STATUTS_VALIDES = {"EN_COURS", "TERMINE", "ERREUR"}


class Execution(Base):
    __tablename__ = "execution"

    id_execution   = Column(Integer,     primary_key=True, autoincrement=True)
    date_execution = Column(DateTime,    default=lambda: datetime.now(timezone.utc))
    status         = Column(String(20),  nullable=False, default="EN_COURS")
    # Historique complet de la boucle superviseur (sérialisé en JSON)
    history_json   = Column(JSONB,       nullable=True)
    # Outputs finaux par agent : { agent_id: message_dict }
    outputs_json   = Column(JSONB,       nullable=True)
    workflow_id    = Column(Integer,     ForeignKey("workflow.id_workflow"), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('EN_COURS','TERMINE','ERREUR')",
            name="ck_execution_status"
        ),
    )

    # Relations
    workflow  = relationship("Workflow",  back_populates="executions")
    messages  = relationship("Message",   back_populates="execution",
                             cascade="all, delete-orphan",
                             order_by="Message.date_creation")
    resultat  = relationship("Resultat",  back_populates="execution",
                             uselist=False,   # 1 résultat max par exécution
                             cascade="all, delete-orphan")

    def __init__(self, workflow_id: int, date_execution: datetime = None):
        self.workflow_id    = workflow_id
        self.status         = "EN_COURS"
        self.date_execution = date_execution or datetime.now(timezone.utc)
        self.history_json   = []
        self.outputs_json   = {}

    # ------------------------------------------------------------------
    # Méthodes métier (conception v2 §3.6)
    # ------------------------------------------------------------------

    def collecterMessage(self, message) -> None:
        """
        Lie un Message à cette exécution.
        La persistance (DB.INSERT) est gérée par la session SQLAlchemy.
        """
        message.execution_id = self.id_execution
        if self.messages is None:
            self.messages = []
        self.messages.append(message)

    def sauvegarderHistorique(self, state: dict) -> None:
        """Persiste l'état final LangGraph (history + outputs)."""
        self.history_json = state.get("history", [])
        self.outputs_json = {
            str(k): v.toDict() if hasattr(v, "toDict") else v
            for k, v in state.get("outputs", {}).items()
        }

    def terminer(self) -> None:
        """Passe le statut à TERMINE."""
        if self.status != "EN_COURS":
            raise ValueError(f"Impossible de terminer depuis le statut : {self.status}")
        self.status = "TERMINE"

    def marquerErreur(self) -> None:
        """Passe le statut à ERREUR."""
        if self.status != "EN_COURS":
            raise ValueError(f"Impossible de marquer en erreur depuis : {self.status}")
        self.status = "ERREUR"

    def transmettreResultats(self) -> dict:
        """Retourne la réponse HTTP complète (conception v2 §3.6.4)."""
        return {
            "id_execution":  self.id_execution,
            "status":        self.status,
            "date_execution": str(self.date_execution),
            "messages": [m.toDict() for m in (self.messages or [])],
            "resultat": self.resultat.toDict() if self.resultat else None,
        }

    def toDict(self) -> dict:
        return {
            "id_execution":   self.id_execution,
            "date_execution": str(self.date_execution),
            "status":         self.status,
            "workflow_id":    self.workflow_id,
            "history_json":   self.history_json,
            "outputs_json":   self.outputs_json,
        }

    def __repr__(self):
        return f"<Execution id={self.id_execution} status={self.status}>"


# ------------------------------------------------------------------
# Classe Resultat — liée à Execution (1-1, conception v2 §3.7)
# ------------------------------------------------------------------

from sqlalchemy import Text, UniqueConstraint


class Resultat(Base):
    __tablename__ = "resultat"

    id_resultat     = Column(Integer,   primary_key=True, autoincrement=True)
    contenu_final   = Column(Text,      nullable=False)
    date_generation = Column(DateTime,  default=lambda: datetime.now(timezone.utc))
    execution_id    = Column(Integer,   ForeignKey("execution.id_execution"),
                             nullable=False, unique=True)

    execution = relationship("Execution", back_populates="resultat")

    def __init__(self, contenu_final: str, execution_id: int,
                 date_generation: datetime = None):
        if not contenu_final:
            raise ValueError("Contenu final vide")
        self.contenu_final   = contenu_final
        self.execution_id    = execution_id
        self.date_generation = date_generation or datetime.now(timezone.utc)

    def exporter(self, format: str) -> bytes:
        """Exporte le résultat en txt, json ou pdf."""
        if format == "txt":
            return self.contenu_final.encode("utf-8")

        if format == "json":
            import json
            data = {
                "id_resultat":    self.id_resultat,
                "contenuFinal":   self.contenu_final,
                "dateGeneration": str(self.date_generation),
            }
            return json.dumps(data, ensure_ascii=False).encode("utf-8")

        if format == "pdf":
            raise NotImplementedError("Export PDF : intégrer PdfGenerator")

        raise ValueError(f"Format non supporté : {format}")

    def toDict(self) -> dict:
        return {
            "id_resultat":     self.id_resultat,
            "contenu_final":   self.contenu_final,
            "date_generation": str(self.date_generation),
            "execution_id":    self.execution_id,
        }

    def __repr__(self):
        return f"<Resultat execution_id={self.execution_id}>"