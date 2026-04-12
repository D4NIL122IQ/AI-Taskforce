# back/appDatabase/init_db.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from backend.appDatabase.database import Base, engine
from backend.models.agent_model import Agent
from backend.models.document_model import Document
from backend.models.execution_model import Execution
from backend.models.workflow_model import Workflow
from backend.models.message_model import Message
from backend.models.mcp_token_model import McpToken

db_initialized = False


def _run_migrations():
    """Applique les migrations sur les tables existantes."""
    with engine.connect() as conn:
        # agent : colonne mcp_type
        try:
            conn.execute(text("ALTER TABLE agent ADD COLUMN IF NOT EXISTS mcp_type VARCHAR(10)"))
        except Exception:
            pass

        # mcp_token : recréer si l'ancienne version (workflow_id) est encore présente
        try:
            cols = [r[0] for r in conn.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='mcp_token'"
            ))]
            if "workflow_id" in cols:
                print("[migration] mcp_token : suppression ancienne version (workflow_id)...")
                conn.execute(text("DROP TABLE IF EXISTS mcp_token CASCADE"))
                print("[migration] mcp_token sera recréée par create_all")
        except Exception as e:
            print(f"[migration] mcp_token check ignoré : {e}")

        conn.commit()


def init():
    global db_initialized
    if db_initialized:
        return

    print("Création des tables...")
    _run_migrations()                      # drop des tables obsolètes avant create_all
    Base.metadata.create_all(bind=engine)  # crée les tables manquantes / nouvelles
    print("Tables créées avec succès !")

    db_initialized = True
    

if __name__ == "__main__":
    init()
