# backend/appDatabase/init_db.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.appDatabase.database import Base, engine
from backend.models.agent_model import AgentModel
from backend.models.document_model import Document
from backend.models.etape_model import Etape
from backend.models.execution_model import Execution
from backend.models.workflow_model import Workflow

from backend.models.message_model import Message

def init():
    print("Création des tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès !")

if __name__ == "__main__":
    init()