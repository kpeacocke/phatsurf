import mongomock
import pytest

from app import create_app
from app.extensions import mongo


@pytest.fixture(scope="function")
def mock_mongo(monkeypatch):
    """
    Replace the MongoDB client with a mongomock instance for testing.
    """
    mocked_client = mongomock.MongoClient()
    mocked_db = mocked_client["test_phatsurf"]  # Use a test database

    # Monkeypatch the `mongo.db` object
    monkeypatch.setattr(mongo, "db", mocked_db)

    yield mocked_db


@pytest.fixture
def app(mock_mongo):
    """
    Create and configure a new app instance for all tests.
    """
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF for testing

    yield app


@pytest.fixture
def client(app):
    """
    A test client for making requests to the app.
    """
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_user():
    """
    Provide a mock user dictionary for use in tests.
    """
    return {"location": "Sydney", "weight": 75.0, "fitness": "Intermediate"}


@pytest.fixture
def mock_surf_condition():
    """
    Provide a mock surf condition dictionary for use in tests.
    """
    return {
        "location": "Sydney",
        "wave_height": 2.5,
        "wind_speed": 15,
        "date": "2024-11-27",
    }
