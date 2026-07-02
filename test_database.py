"""
Tests for database.py — connection, session factory, and table creation.

Run with: pytest test_database.py -v
"""
import pytest
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from database import engine, SessionLocal, Base
import models  # noqa: F401 — must import so Base.metadata knows about your tables


def test_engine_connects():
    """Engine can open a raw connection to the configured database."""
    with engine.connect() as conn:
        assert conn is not None


def test_engine_can_execute_query():
    """Connection can actually run a trivial query against Postgres."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_session_factory_produces_session():
    """SessionLocal() yields a usable SQLAlchemy Session."""
    db = SessionLocal()
    try:
        assert isinstance(db, Session)
    finally:
        db.close()


def test_models_registered_on_base():
    """Model classes defined against Base are registered in its metadata."""
    assert len(Base.metadata.tables) > 0, (
        "No tables found on Base.metadata — check that models.py "
        "is being imported before this runs."
    )


def test_tables_exist_in_database():
    """Every table declared in models.py actually exists in Postgres.

    This will fail if you forgot to run Base.metadata.create_all(bind=engine)
    somewhere (e.g. in main.py) before the app/tests run.
    """
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    for table_name in Base.metadata.tables:
        assert table_name in existing_tables, (
            f"Table '{table_name}' is defined in models.py but doesn't "
            f"exist in the database yet."
        )


def test_session_rolls_back_cleanly():
    """A session can be opened, used, and rolled back without error.

    Rolling back instead of committing keeps this test from leaving
    junk data behind in your real database.
    """
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db.rollback()
    finally:
        db.close()
