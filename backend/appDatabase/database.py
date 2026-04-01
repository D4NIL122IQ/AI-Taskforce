from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus

# quote_plus encode les caractères spéciaux et accentués
mot_de_passe = quote_plus("passer")

DATABASE_URL = f"postgresql://postgres:{mot_de_passe}@localhost:5432/ai_taskforce"

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