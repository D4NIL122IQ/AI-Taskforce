# back/init_db.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from back.database import Base, engine
from back.models.message import Message

def init():
    print("Création des tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès !")

if __name__ == "__main__":
    init()