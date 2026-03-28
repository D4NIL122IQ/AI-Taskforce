import os
import sys
import pytest
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from back.appDatabase.database import Base
from back.models.utilisateur_model import Utilisateur


from back.models.agent_model import Agent
from back.models.document_model import Document
from back.models.etape_model import Etape
from back.models.execution_model import Execution, Resultat
from back.models.message_model import Message
from back.models.workflow_model import Workflow

mot_de_passe = quote_plus("passer123")
TEST_DB_URL = "postgresql+psycopg://postgres:" + mot_de_passe + "@localhost:5432/ai_taskforce"

@pytest.fixture(scope="session")
def engine():
    eng = create_engine(TEST_DB_URL, echo=False)
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()

@pytest.fixture(scope="function")
def session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    sess = sessionmaker(bind=connection)()
    sess.begin_nested()
    yield sess
    sess.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def agent_actif(session):
    agent = Agent(nom="Agent Test", modele="Openai", temperature=0.5, max_tokens=512)
    session.add(agent)
    session.commit()
    return agent

@pytest.fixture
def workflow_simple(session, agent_actif):
    wf = Workflow(nom="Workflow Test", superviseur_id=agent_actif.id_agent)
    session.add(wf)
    session.commit()
    return wf

@pytest.fixture
def execution_en_cours(session, workflow_simple):
    exec_ = Execution(workflow_id=workflow_simple.id_workflow, status="EN_COURS")
    session.add(exec_)
    session.commit()
    return exec_
