import mongomock
import pytest

from app.extensions import mongo
from app.models import create_user, get_users


@pytest.fixture(scope="function", autouse=True)
def mock_mongo_instance():
    """
    Replace MongoDB with a mongomock instance for isolated testing.
    """
    mock_db = mongomock.MongoClient().db
    mongo.db = mock_db  # Inject the mocked database into the `mongo` extension
    return mock_db


def test_create_user(mock_mongo_instance, mock_user):
    """
    Test inserting a user into the database via `create_user`.
    """
    result = create_user(mock_user)
    assert result.inserted_id is not None

    # Verify that the user exists in the database
    inserted_user = mongo.db.users.find_one({"_id": result.inserted_id})
    assert inserted_user is not None
    assert inserted_user["location"] == mock_user["location"]
    assert inserted_user["weight"] == mock_user["weight"]
    assert inserted_user["fitness"] == mock_user["fitness"]


def test_get_users(mock_mongo_instance, mock_user):
    """
    Test retrieving users from the database via `get_users`.
    """
    # Insert a test user
    create_user(mock_user)

    # Retrieve all users
    users = get_users()
    assert len(users) == 1
    assert users[0]["location"] == mock_user["location"]
    assert users[0]["weight"] == mock_user["weight"]
    assert users[0]["fitness"] == mock_user["fitness"]

    # Ensure no additional users exist
    assert len(list(users)) == 1
