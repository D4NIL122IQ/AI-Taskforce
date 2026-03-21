from sqlalchemy import Column, Integer, String, Float, Text, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from back.database import Base


class Agent(Base):
    __tablename__ = "agent"

    id_agent      = Column(Integer, primary_key=True, autoincrement=True)
    nom           = Column(String(100), nullable=False)
    role          = Column(Text, nullable=True)
    modele        = Column(String(50), nullable=False)
    temperature   = Column(Float, nullable=False, default=0.7)
    max_tokens    = Column(Integer, nullable=False, default=1024)
    system_prompt = Column(Text, nullable=True)
    date_creation = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    statut        = Column(String(20), default="ACTIF")

    __table_args__ = (
        CheckConstraint(
            "modele IN ('Openai','Ollama','Mistral')",
            name="ck_agent_modele",
        ),
        CheckConstraint(
            "temperature >= 0.0 AND temperature <= 1.0",
            name="ck_agent_temperature",
        ),
        CheckConstraint(
            "max_tokens >= 1 AND max_tokens <= 8192",
            name="ck_agent_max_tokens",
        ),
        CheckConstraint(
            "statut IN ('ACTIF','INTERROMPU')",
            name="ck_agent_statut",
        ),
    )

    documents      = relationship("Document", back_populates="agent", cascade="all, delete-orphan")
    etapes         = relationship("Etape",    back_populates="agent")
    superviseur_de = relationship(
        "Workflow",
        foreign_keys="[Workflow.superviseur_id]",
        back_populates="superviseur"
    )

    def ajouterDocument(self, doc) -> None:
        if doc in self.documents:
            raise ValueError("Document déjà attaché à cet agent")
        self.documents.append(doc)

    def modifierParametre(self, champ: str, valeur) -> None:
        champs_autorises = {"nom", "role", "modele", "temperature", "max_tokens", "system_prompt"}
        if champ not in champs_autorises:
            raise ValueError(f"Champ inconnu : {champ}")
        setattr(self, champ, valeur)

    def killProcess(self) -> None:
        if hasattr(self, "_execution_task") and self._execution_task:
            self._execution_task.cancel()
            self._execution_task = None
        self.statut = "INTERROMPU"

    def __repr__(self):
        return f"<Agent id={self.id_agent} nom={self.nom} modele={self.modele}>"