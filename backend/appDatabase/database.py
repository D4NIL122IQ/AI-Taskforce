from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus
import os

mot_de_passe = quote_plus("passer")

DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://postgres:{mot_de_passe}@localhost:5432/ai_taskforce") #f"postgresql://postgres:{mot_de_passe}@localhost:5432/ai_taskforce"

# URL vers la base par défaut pour pouvoir créer ai_taskforce si besoin
DEFAULT_URL = f"postgresql://postgres:{mot_de_passe}@localhost:5432/postgres"

def create_database_if_not_exists():
    try:
        default_engine = create_engine(DEFAULT_URL, isolation_level="AUTOCOMMIT")
        with default_engine.connect() as conn:
            result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'ai_taskforce'"))
            if not result.fetchone():
                conn.execute(text("CREATE DATABASE ai_taskforce"))
                print("Base de données 'ai_taskforce' créée avec succès !")
            else:
                print("Base de données 'ai_taskforce' existe déjà.")
        default_engine.dispose()
    except Exception as e:
        print(f"Erreur lors de la création de la base : {e}")
        raise

create_database_if_not_exists()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)