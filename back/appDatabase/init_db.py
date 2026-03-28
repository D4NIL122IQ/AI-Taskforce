# back/init_db.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from back.appDatabase.database import Base, engine
from back.models.utilisateur_model import Utilisateur
from back.models.agent_model import Agent
from back.models.document_model import Document
from back.models.etape_model import Etape
from back.models.execution_model import Execution
from back.models.workflow_model import Workflow

from back.models.message_model import Message

def init():
    print("CrÃ©ation des tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables crÃ©Ã©es avec succÃ¨s !")

if __name__ == "__main__":
    init()
