import os
import sys
import pytest

# Ensure backend root is in python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

parent_dir = os.path.abspath(os.path.join(backend_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.database.session import Base, engine, SessionLocal
from sample_data.seed_data import seed_database

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Creates tables and seeds test institutions before tests run.
    """
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield
