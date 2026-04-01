from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from back.appDatabase.database import Base

TYPES_VALIDES = {"user_input", "agent_response", "system"}


class Message(Base):
    __tablename__ = "message"

    id            = Column(Integer,     primary_key=True, autoincrement=True)
    contenu       = Column(Text,        nullable=False)
    date_creation = Column(DateTime,    default=lambda: datetime.now(timezone.utc))
    type          = Column(String(30),  nullable=False)
    expediteur    = Column(String(100), nullable=False)
    execution_id  = Column(Integer, ForeignKey("execution.id_execution"), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "type IN ('user_input','agent_response','system')",
            name="ck_message_type"
        ),
    )
    execution = relationship("Execution", back_populates="messages")