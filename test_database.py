from sqlalchemy import inspect
from sqlalchemy.orm import Session

from database import engine, SessionLocal, Base
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from database import engine, SessionLocal, Base


def test_engine_connects():
    """Engine can open a raw connection to the configured database."""
    with engine.connect() as conn:
        assert conn is not None


def test_session_factory_produces_session():
    """SessionLocal() yields a usable SQLAlchemy Session."""
    db = SessionLocal()
    try:
        assert isinstance(db, Session)
    finally:
        db.close()


def test_models_registered_on_base():
    """Any model classes defined against Base show up in its metadata."""
    inspector = inspect(engine)
    # Sanity check only — replace with real table name assertions
    # once models.py table names are finalized, e.g.:
    # assert "users" in Base.metadata.tables
    assert Base.metadata is not None


def test_engine_connects():
    """Engine can open a raw connection to the configured database."""
    with engine.connect() as conn:
        assert conn is not None


def test_session_factory_produces_session():
    """SessionLocal() yields a usable SQLAlchemy Session."""
    db = SessionLocal()
    try:
        assert isinstance(db, Session)
    finally:
        db.close()


def test_models_registered_on_base():
    """Any model classes defined against Base show up in its metadata."""
    inspector = inspect(engine)
    # Sanity check only — replace with real table name assertions
    # once models.py table names are finalized, e.g.:
    # assert "users" in Base.metadata.tables
    assert Base.metadata is not None
