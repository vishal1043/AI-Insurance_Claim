# backend/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

# Use psycopg3 driver for PostgreSQL
# You can also move this to .env as DATABASE_URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    
)

if not DATABASE_URL:
    raise Exception("DATABASE_URL not found in .env file")

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True,   # shows SQLs in console (helpful for debugging)
)

# Create SessionLocal class (session = SessionLocal())
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for SQLAlchemy ORM models
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    """FastAPI dependency that provides a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
