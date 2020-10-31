import os
from pathlib import Path

from app import app
from db import db
import pytest


@pytest.fixture(scope="session")
def client():
    global db_path
    cwd = Path(os.getcwd())
    db_path = cwd.parent / "test.db"
    if db_path.exists():
        os.remove(db_path)
    app.testing = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    test_client = app.test_client()
    app.app_context()
    app.app_context().push()
    db.init_app(app)
    db.create_all()
    yield test_client


def pytest_sessionfinish(session):
    os.remove(db_path)