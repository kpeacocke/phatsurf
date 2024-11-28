import pytest
from app import create_app
from app.extensions import mongo

@pytest.fixture(autouse=True)
def set_testing_env(monkeypatch):
    """
    Set TESTING=True for all tests to ensure `.env` is ignored.
    """
    monkeypatch.setenv("TESTING", "True")


@pytest.fixture
def app():
    """
    Create and configure a new app instance for each test.
    """
    app = create_app()
    app.config["TESTING"] = True
    app.config["MONGO_URI"] = "mongodb://localhost:27017/test_phatsurf"

    with app.app_context():
        # Clear the database collections before each test
        mongo.db.users.delete_many({})
        mongo.db.surf_conditions.delete_many({})
    return app


@pytest.fixture
def client(app):
    """
    A test client for making requests to the app.
    """
    return app.test_client()


@pytest.fixture
def mock_user():
    """
    Provide a mock user dictionary for use in tests.
    """
    return {
        "location": "Sydney",
        "weight": 75.0,
        "fitness": "Intermediate"
    }


@pytest.fixture
def mock_surf_condition():
    """
    Provide a mock surf condition dictionary for use in tests.
    """
    return {
        "location": "Sydney",
        "wave_height": 2.5,
        "wind_speed": 15,
        "date": "2024-11-27"
    }
