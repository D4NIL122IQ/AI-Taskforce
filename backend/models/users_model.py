from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from back.appDatabase.database  import Base
import bcrypt


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    mot_de_passe = Column(String(255), nullable=False)
    date_creation = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    agents = relationship("AgentModel", back_populates="users", cascade="all, delete-orphan")
    workflows = relationship("Workflow", back_populates="users", cascade="all, delete-orphan")