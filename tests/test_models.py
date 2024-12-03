from app.models import create_user, get_users


def test_create_user(app, mock_user):
    """
    Test inserting a user into the database via `create_user`.
    """
    result = create_user(mock_user)
    assert result.inserted_id is not None


def test_get_users(app, mock_user):
    """
    Test retrieving users from the database via `get_users`.
    """
    # Insert a test user
    create_user(mock_user)

    # Retrieve all users
    users = get_users()
    assert len(users) == 1
    assert users[0]["location"] == "Sydney"
