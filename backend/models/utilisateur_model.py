from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.appDatabase.database import Base
import bcrypt


class Utilisateur(Base):
    __tablename__ = "utilisateur"

    id_utilisateur = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    mot_de_passe = Column(String(255), nullable=False)
    date_creation = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    agents = relationship("Agent", back_populates="utilisateur", cascade="all, delete-orphan")
    workflows = relationship("Workflow", back_populates="utilisateur", cascade="all, delete-orphan")