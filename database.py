from sqlalchemy.orm import Session
from models import engine, SessionLocal

def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()