import mongomock
import pytest

from app import create_app
from app.extensions import mongo


@pytest.fixture(scope="function")
def mock_mongo(monkeypatch):
    """
    Replace the MongoDB client with a mongomock instance for testing.
    """
    # Create a mocked MongoDB client and database
    mocked_client = mongomock.MongoClient()
    mocked_db = mocked_client["test_phatsurf"]

    # Patch the PyMongo extension to use the mocked client and database
    monkeypatch.setattr(mongo, "cx", mocked_client)
    monkeypatch.setattr(mongo, "db", mocked_db)
    monkeypatch.setattr(mongo, "init_app", lambda app: None)
    monkeypatch.setattr(mongo, "init_app", lambda app: None)

    yield mocked_db


@pytest.fixture
def app(mock_mongo):
    """
    Create and configure a new app instance for all tests.
    """
    app = create_app()
    app.config["TESTING"] = True
    app.config["MONGO_URI"] = None  # Prevent any real database connection
    # file deepcode ignore DisablesCSRFProtection/test: <Disabling CSRF for testing>
    app.config["WTF_CSRF_ENABLED"] = False  # NOSONAR: SCS001 - Allowed for testing
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


@pytest.fixture(autouse=True)
def clear_mock_mongo(mock_mongo):
    """
    Clear the mock database before each test to ensure test isolation.
    """
    mock_mongo.client.drop_database("test_phatsurf")
