"""Database connection and models."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models import Base
from .seed import seed_demo_data as _seed

# Database URL from environment or default to SQLite
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite:///./compliance_demo.db"
)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session."""
    return SessionLocal()


def seed_demo_data():
    """Seed database with demo data."""
    db = SessionLocal()
    try:
        _seed(db)
        db.commit()
    finally:
        db.close()


__all__ = ["get_db", "seed_demo_data", "Base"]
