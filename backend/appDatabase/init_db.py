from backend.appDatabase.database import Base, engine
from backend.models.agent_model import Agent
from backend.models.document_model import Document
from backend.models.etape_model import Etape
from backend.models.execution_model import Execution, Resultat
from backend.models.message_model import Message
from backend.models.utilisateur_model import Utilisateur
from backend.models.workflow_model import Workflow


def init():
    print("Creation des tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables creees avec succes !")


if __name__ == "__main__":
    init()
