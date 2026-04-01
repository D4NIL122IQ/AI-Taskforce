# back/appDatabase/init_db.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from back.appDatabase.database import Base, engine
from back.models.users_model import User
from back.models.agent_model import AgentModel
from back.models.document_model import Document
from back.models.etape_model import Etape
from back.models.execution_model import Execution
from back.models.workflow_model import Workflow

from back.models.message_model import Message

db_initialized = False

def init():
    global db_initialized
    if db_initialized:
        print("la base deja initialisée")
        return
    
    print("Création des tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès !")

    db_initialized = True
    

if __name__ == "__main__":
    init()