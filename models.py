from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./government_data.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(String, unique=True, index=True)
    agency_name = Column(String, index=True)
    recipient_name = Column(String, index=True)
    description = Column(Text)
    award_amount = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    place_of_performance = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Grant(Base):
    __tablename__ = "grants"
    
    id = Column(Integer, primary_key=True, index=True)
    grant_id = Column(String, unique=True, index=True)
    agency_name = Column(String, index=True)
    recipient_name = Column(String, index=True)
    title = Column(String)
    description = Column(Text)
    award_amount = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    category = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Agency(Base):
    __tablename__ = "agencies"
    
    id = Column(Integer, primary_key=True, index=True)
    agency_code = Column(String, unique=True, index=True)
    agency_name = Column(String, index=True)
    total_contracts = Column(Integer, default=0)
    total_grants = Column(Integer, default=0)
    total_spending = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)