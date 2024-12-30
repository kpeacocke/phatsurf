from bson import ObjectId

def test_create_user_success(client, mock_user, mock_mongo):
    """
    Test creating a new user successfully via the `/users` endpoint.
    """
    response = client.post("/users", json=mock_user)
    assert response.status_code == 201, f"Unexpected response: {response.json}"

    # Verify the user was stored in the mock database
    stored_user = mock_mongo.users.find_one({"_id": ObjectId(response.json["user_id"])})
    assert stored_user is not None
    assert stored_user["location"] == mock_user["location"]
    assert stored_user["weight"] == mock_user["weight"]
    assert stored_user["fitness"] == mock_user["fitness"]


def test_create_user_missing_fields(client):
    """
    Test creating a user with missing required fields via the `/users` endpoint.
    """
    invalid_user = {"location": "Sydney"}  # Missing weight and fitness
    response = client.post("/users", json=invalid_user)
    assert response.status_code == 400
    assert "error" in response.json
    assert "Missing or empty fields" in response.json["error"]
    assert "weight" in response.json["error"]
    assert "fitness" in response.json["error"]


def test_create_user_empty_body(client):
    """
    Test creating a user with an empty request body via the `/users` endpoint.
    """
    response = client.post("/users", json={})
    assert response.status_code == 400
    assert response.json["error"] == "Request body is empty"


def test_get_users_success(client, mock_user, mock_mongo):
    """
    Test retrieving all users via the `/users` endpoint after creating a user.
    """
    # Add a test user
    client.post("/users", json=mock_user)

    # Retrieve all users
    response = client.get("/users")
    assert response.status_code == 200
    users = response.json
    assert len(users) == 1
    assert users[0]["location"] == mock_user["location"]
    assert users[0]["weight"] == mock_user["weight"]
    assert users[0]["fitness"] == mock_user["fitness"]

    # Verify the database content matches
    stored_users = list(mock_mongo.users.find())
    assert len(stored_users) == 1
    assert stored_users[0]["location"] == mock_user["location"]
    assert stored_users[0]["weight"] == mock_user["weight"]
    assert stored_users[0]["fitness"] == mock_user["fitness"]


def test_get_users_empty(client, mock_mongo):
    """
    Test retrieving all users when no users exist in the database.
    """
    response = client.get("/users")
    assert response.status_code == 200
    users = response.json
    assert len(users) == 0

    # Verify the database is empty
    stored_users = list(mock_mongo.users.find())
    assert len(stored_users) == 0


def test_health_check(client):
    """
    Test the `/health` endpoint to ensure it reports healthy status.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_get_user_by_id_success(client, mock_user, mock_mongo):
    """
    Test retrieving a user by ID via the `/users/<user_id>` endpoint.
    """
    # Add a test user and retrieve its ID
    response = client.post("/users", json=mock_user)
    user_id = response.json["user_id"]

    # Retrieve the user by ID
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    user = response.json
    assert user["id"] == user_id
    assert user["location"] == mock_user["location"]
    assert user["weight"] == mock_user["weight"]
    assert user["fitness"] == mock_user["fitness"]


def test_get_user_by_id_not_found(client):
    """
    Test retrieving a non-existent user by ID via the `/users/<user_id>` endpoint.
    """
    invalid_user_id = "64cd9f2e3d5a9b14f31a0000"  # Random ObjectId
    response = client.get(f"/users/{invalid_user_id}")
    assert response.status_code == 404
    assert response.json["error"] == "User not found"
