from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.appDatabase.database import get_db
from backend.models.document_model import Document
