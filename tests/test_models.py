import mongomock
import pytest
from bson import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import mongo
from app.models import (
    User,
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_users,
)


def get_mock_db():
    """
    Create and return a new mongomock database instance.
    """
    client = mongomock.MongoClient()
    return client.db


@pytest.fixture(autouse=True)
def mock_mongo(monkeypatch):
    """
    Automatically replace the mongo.db attribute with a mongomock instance.
    """
    mock_db = get_mock_db()
    monkeypatch.setattr(mongo, "db", mock_db)
    return mock_db


@pytest.fixture
def mock_user():
    """
    Provide a sample user dictionary for testing.
    """
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "secret",  # create_user will hash this
        "location": "Nowhere",
        "weight": 150,
        "fitness": "average",
    }


def test_create_user(mock_mongo, mock_user):
    """
    Test inserting a user into the database via `create_user`.
    """
    inserted_id = create_user(mock_user)
    # Verify a non-empty inserted_id string was returned.
    assert inserted_id

    # Verify that the user exists in the mocked database.
    inserted_user = mongo.db.users.find_one({"_id": ObjectId(inserted_id)})
    assert inserted_user is not None
    # Check that stored values match input (except password, which is hashed).
    assert inserted_user["username"] == mock_user["username"]
    assert inserted_user["email"] == mock_user["email"]
    assert inserted_user["location"] == mock_user["location"]
    assert inserted_user["weight"] == mock_user["weight"]
    assert inserted_user["fitness"] == mock_user["fitness"]


def test_get_users(mock_mongo, mock_user):
    """
    Test retrieving users from the database via `get_users`.
    """
    # Insert a test user.
    create_user(mock_user)

    # Retrieve all users.
    users = get_users()
    users_list = list(users)
    # Ensure exactly one user is returned.
    assert len(users_list) == 1
    user = users_list[0]
    assert user["username"] == mock_user["username"]
    assert user["email"] == mock_user["email"]
    assert user["location"] == mock_user["location"]
    assert user["weight"] == mock_user["weight"]
    assert user["fitness"] == mock_user["fitness"]


def test_user_model_initialization():
    """
    Test the initialization of the User model to verify that:
      - The `id` attribute is set as a string.
      - All other attributes are correctly assigned.
    """
    user_id = (
        123  # Even if an integer is provided, the model should store this as a string.
    )
    username = "sampleuser"
    email = "sample@example.com"
    password_hash = "hashedpassword"
    location = "Sampletown"
    weight = 180
    fitness = "excellent"

    user = User(user_id, username, email, password_hash, location, weight, fitness)

    # Verify that `id` is stored as a string
    assert user.id == str(user_id)
    assert isinstance(user.id, str)

    # Verify the remaining attributes are set correctly
    assert user.username == username
    assert user.email == email
    assert user.password_hash == password_hash
    assert user.location == location
    assert user.weight == weight
    assert user.fitness == fitness


def test_check_password():
    """
    Test the check_password method of the User model.
    """
    safe_pwd = "UncompromisedPassword456$%^"
    hashed = generate_password_hash(safe_pwd)
    user = User(1, "testuser", "test@example.com", hashed, "Nowhere", 150, "average")

    # Correct password should return True
    assert user.check_password(safe_pwd)
    # Incorrect password should return False
    assert not user.check_password("wrongpassword")


def test_from_mongo_none():
    """
    Test User.from_mongo with None to ensure it returns None.
    """
    user = User.from_mongo(None)
    assert user is None


def test_from_mongo_valid():
    """
    Test User.from_mongo with valid user_data.
    """
    user_data = {
        "_id": ObjectId("507f191e810c19729de860ea"),
        "username": "frommongo",
        "email": "mongo@example.com",
        "password": "hashedpass",
        "location": "City",
        "weight": 200,
        "fitness": "good",
    }
    user = User.from_mongo(user_data)
    assert user is not None
    assert user.id == str(user_data["_id"])
    assert user.username == user_data["username"]
    assert user.email == user_data["email"]
    assert user.password_hash == user_data["password"]
    assert user.location == user_data["location"]
    assert user.weight == user_data["weight"]
    assert user.fitness == user_data["fitness"]


def test_get_user_by_id_success(mock_mongo, mock_user):
    """
    Test get_user_by_id returns a valid User object when the user exists.
    """
    inserted_id = create_user(mock_user)
    user = get_user_by_id(inserted_id)
    assert user is not None
    assert user.email == mock_user["email"]


def test_get_user_by_id_nonexistent(mock_mongo):
    """
    Test get_user_by_id returns None when the user does not exist.
    """
    fake_id = str(ObjectId())
    user = get_user_by_id(fake_id)
    assert user is None


def test_get_user_by_id_invalid(mock_mongo):
    """
    Test get_user_by_id returns None when an invalid user_id is provided.
    This will trigger an exception during ObjectId conversion.
    """
    user = get_user_by_id("invalid_id")
    assert user is None


def test_get_user_by_id_exception(monkeypatch, mock_mongo):
    """
    Test get_user_by_id handles exceptions (simulated by monkeypatching)
    and returns None.
    """

    def fake_find_one(query):
        raise RuntimeError("Simulated exception")

    monkeypatch.setattr(mongo.db.users, "find_one", fake_find_one)
    user = get_user_by_id(str(ObjectId()))
    assert user is None


def test_get_user_by_email_success(mock_mongo, mock_user):
    """
    Test get_user_by_email returns a valid User object when the user exists.
    """
    create_user(mock_user)
    user = get_user_by_email(mock_user["email"])
    assert user is not None
    assert user.username == mock_user["username"]


def test_get_user_by_email_nonexistent(mock_mongo):
    """
    Test get_user_by_email returns None when no user with the given email exists.
    """
    user = get_user_by_email("nonexistent@example.com")
    assert user is None


def test_get_user_by_email_exception(monkeypatch, mock_mongo):
    """
    Test get_user_by_email handles exceptions (simulated by monkeypatching)
    and returns None.
    """

    def fake_find_one(query):
        raise RuntimeError("Simulated exception")

    monkeypatch.setattr(mongo.db.users, "find_one", fake_find_one)
    user = get_user_by_email("test@example.com")
    assert user is None


def test_create_user_password_hashing(mock_mongo, mock_user):
    """
    Test that when a user is created with a "password" key,
    the plain-text password is replaced with a hashed version.
    """
    plain_password = mock_user["password"]
    inserted_id = create_user(mock_user)
    inserted_user = mongo.db.users.find_one({"_id": ObjectId(inserted_id)})

    # Ensure the stored password is not the plain text
    assert inserted_user["password"] != plain_password

    # Verify that the stored hash matches the plain password using check_password_hash
    assert check_password_hash(inserted_user["password"], plain_password)


def test_create_user_without_password(mock_mongo, mock_user):
    """
    Test that when a user is created without a "password" key,
    the branch for hashing is not executed, and the resulting document
    does not include a "password" field.
    """
    # Remove the "password" key from the user data.
    user_data = mock_user.copy()
    user_data.pop("password", None)

    inserted_id = create_user(user_data)
    inserted_user = mongo.db.users.find_one({"_id": ObjectId(inserted_id)})

    # The document should not have a "password" key.
    assert "password" not in inserted_user
