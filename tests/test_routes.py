def test_create_user_success(client, mock_user):
    """
    Test creating a new user successfully via the `/users` endpoint.
    """
    response = client.post("/users", json=mock_user)
    assert response.status_code == 201
    assert response.json["message"] == "User created"
    assert "user_id" in response.json  # Verify user_id is returned


def test_create_user_invalid_data(client):
    """
    Test creating a user with invalid data via the `/users` endpoint.
    """
    invalid_user = {
        "location": "Sydney"  # Missing weight and fitness
    }
    response = client.post("/users", json=invalid_user)
    assert response.status_code == 400
    assert "error" in response.json
    assert response.json["error"] == "Missing fields: weight, fitness"


def test_get_users_success(client, mock_user):
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


def test_get_users_empty(client):
    """
    Test retrieving all users when no users exist in the database.
    """
    response = client.get("/users")
    assert response.status_code == 200
    users = response.json
    assert len(users) == 0
