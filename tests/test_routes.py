# tests/test_routes.py
import pytest


# A dummy user class with Flask-Login required properties.
class DummyUser:
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self._password = password

    def check_password(self, password):
        # In tests, we simply compare plaintext.
        return self._password == password

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


@pytest.fixture
def client():
    """Create and configure a new app instance for each test."""
    from app import create_app  # your application factory

    app = create_app(testing=True)
    with app.app_context():
        with app.test_client() as client:
            yield client


# ================= JSON Endpoint Tests =================


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "healthy"


def test_register_success(client, monkeypatch):
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    }
    # Ensure no user exists with this email.
    monkeypatch.setattr("app.routes.get_user_by_email", lambda email: None)
    # Patch create_user to simply return a fake user id.
    fake_user_id = "fakeid123"
    monkeypatch.setattr("app.routes.create_user", lambda user_data: fake_user_id)
    response = client.post("/register", json=data)
    assert response.status_code == 201, f"Response: {response.get_data(as_text=True)}"
    json_data = response.get_json()
    assert json_data.get("message") == "User registered"
    assert json_data.get("user_id") == fake_user_id


def test_register_missing_fields(client):
    # Branch: missing required fields for /register JSON
    data = {"username": "testuser", "email": "test@example.com"}  # missing password
    response = client.post("/register", json=data)
    assert response.status_code == 400, f"Response: {response.get_data(as_text=True)}"
    json_data = response.get_json()
    assert json_data is not None
    assert "error" in json_data


def test_register_existing_email(client, monkeypatch):
    # Branch: email already exists for /register JSON
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    }
    monkeypatch.setattr("app.routes.get_user_by_email", lambda email: object())
    response = client.post("/register", json=data)
    assert response.status_code == 400, f"Response: {response.get_data(as_text=True)}"
    json_data = response.get_json()
    assert json_data is not None
    assert "error" in json_data


def test_register_exception_json(client, monkeypatch):
    # Branch: Exception in /register JSON route returns ERROR_TRY_AGAIN.
    from app.routes import ERROR_TRY_AGAIN

    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    }
    monkeypatch.setattr("app.routes.get_user_by_email", lambda email: None)
    # Force an exception in create_user.
    monkeypatch.setattr("app.routes.create_user", lambda user_data: 1 / 0)
    response = client.post("/register", json=data)
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data.get("error") == ERROR_TRY_AGAIN


def test_login_success(client, monkeypatch):
    data = {"email": "test@example.com", "password": "password123"}
    dummy_user = DummyUser("dummyid", "testuser", "test@example.com", "password123")
    monkeypatch.setattr(
        "app.routes.get_user_by_email",
        lambda email: dummy_user if email == data["email"] else None,
    )
    response = client.post("/login", json=data)
    assert response.status_code == 200, f"Response: {response.get_data(as_text=True)}"
    json_data = response.get_json()
    assert json_data.get("message") == "Login successful"
    assert json_data.get("user_id") == dummy_user.id


def test_login_failure(client, monkeypatch):
    data = {"email": "test@example.com", "password": "wrongpassword"}
    dummy_user = DummyUser("dummyid", "testuser", "test@example.com", "password123")
    monkeypatch.setattr(
        "app.routes.get_user_by_email",
        lambda email: dummy_user if email == data["email"] else None,
    )
    response = client.post("/login", json=data)
    assert response.status_code == 401, f"Response: {response.get_data(as_text=True)}"
    json_data = response.get_json()
    assert json_data is not None
    assert "error" in json_data


def test_login_exception_json(client, monkeypatch):
    # Branch: Exception in /login JSON route.
    from app.routes import ERROR_TRY_AGAIN

    data = {"email": "test@example.com", "password": "password123"}
    monkeypatch.setattr("app.routes.get_user_by_email", lambda email: 1 / 0)
    response = client.post("/login", json=data)
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data.get("error") == ERROR_TRY_AGAIN


def test_logout_success(client, monkeypatch):
    dummy_user = DummyUser("dummyid", "testuser", "test@example.com", "password123")
    monkeypatch.setattr(
        "app.routes.get_user_by_id",
        lambda user_id: dummy_user if user_id == dummy_user.id else None,
    )
    with client.session_transaction() as sess:
        sess["user_id"] = dummy_user.id
        sess["_user_id"] = dummy_user.id
        sess["_fresh"] = True
    # No need to call login_user; the session is already set.
    response = client.get("/logout")
    assert response.status_code == 200, f"Response: {response.get_data(as_text=True)}"
    json_data = response.get_json()
    assert json_data.get("message") == "Logout successful"


def test_profile_success(client, monkeypatch):
    dummy_user = DummyUser("dummyid", "testuser", "test@example.com", "password123")
    monkeypatch.setattr(
        "app.routes.get_user_by_id",
        lambda user_id: dummy_user if user_id == dummy_user.id else None,
    )
    with client.session_transaction() as sess:
        sess["user_id"] = dummy_user.id
        sess["_user_id"] = dummy_user.id
    response = client.get("/profile")
    assert response.status_code == 200, f"Response: {response.get_data(as_text=True)}"
    json_data = response.get_json()
    assert json_data.get("id") == dummy_user.id
    assert json_data.get("username") == dummy_user.username
    assert json_data.get("email") == dummy_user.email


def test_profile_not_found(client, monkeypatch):
    # Branch: /profile returns 404 if user not found.
    dummy_user = DummyUser("dummyid", "testuser", "test@example.com", "password123")
    # Force get_user_by_id (used in the profile route) to return None.
    monkeypatch.setattr("app.routes.get_user_by_id", lambda user_id: None)
    # Override Flask-Login's internal _get_user to return dummy_user,
    # ensuring that login_required passes.
    monkeypatch.setattr("flask_login.utils._get_user", lambda: dummy_user)
    with client.session_transaction() as sess:
        sess["user_id"] = dummy_user.id
        sess["_user_id"] = dummy_user.id
    response = client.get("/profile")
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data.get("error") == "User not found"


def test_profile_exception(client, monkeypatch):
    from app.routes import ERROR_MESSAGE

    dummy_user = DummyUser("dummyid", "testuser", "test@example.com", "password123")
    # Override Flask-Login's _get_user so that current_user is our dummy user.
    monkeypatch.setattr("flask_login.utils._get_user", lambda: dummy_user)
    # Force get_user_by_id (called in /profile) to raise an exception.
    monkeypatch.setattr(
        "app.routes.get_user_by_id",
        lambda user_id: (_ for _ in ()).throw(RuntimeError("Forced exception")),
    )
    with client.session_transaction() as sess:
        sess["user_id"] = dummy_user.id
        sess["_user_id"] = dummy_user.id
    response = client.get("/profile")
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data.get("error") == ERROR_MESSAGE


def test_get_users_exception(client, monkeypatch):
    # Branch: Exception in GET /users.
    from app.routes import ERROR_MESSAGE

    class FakeUsersCollection:
        def find(self):
            raise RuntimeError("Forced exception")

    fake_db = type("FakeDB", (), {"users": FakeUsersCollection()})()
    monkeypatch.setattr("app.routes.mongo.db", fake_db)
    dummy_user = DummyUser("dummyid", "testuser", "test@example.com", "password123")
    monkeypatch.setattr(
        "app.routes.get_user_by_id",
        lambda uid: dummy_user if uid == dummy_user.id else None,
    )
    with client.session_transaction() as sess:
        sess["user_id"] = dummy_user.id
        sess["_user_id"] = dummy_user.id
    response = client.get("/users")
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data.get("error") == ERROR_MESSAGE


def test_create_user_missing_fields_json(client, monkeypatch):
    # Branch: Missing required fields in POST /users.
    data = {
        "username": "incomplete",
        "email": "incomplete@example.com",
    }  # missing password
    dummy_user = DummyUser("dummyid", "testuser", "test@example.com", "password123")
    # Ensure that Flask-Login considers the user authenticated.
    monkeypatch.setattr("flask_login.utils._get_user", lambda: dummy_user)
    with client.session_transaction() as sess:
        sess["user_id"] = dummy_user.id
        sess["_user_id"] = dummy_user.id
    response = client.post("/users", json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data.get("error") == "Missing required fields"


# Removed duplicate test_create_user_missing_fields_json to avoid redefinition error.


def test_get_user_by_id_not_found(client, monkeypatch):
    # Force get_user_by_id to return None.
    monkeypatch.setattr("app.routes.get_user_by_id", lambda user_id: None)
    dummy_user = DummyUser("dummyid", "testuser", "test@example.com", "password123")
    # Override Flask-Login's _get_user so that the login_required decorator passes.
    monkeypatch.setattr("flask_login.utils._get_user", lambda: dummy_user)
    with client.session_transaction() as sess:
        sess["user_id"] = dummy_user.id
        sess["_user_id"] = dummy_user.id
    response = client.get("/users/nonexistent")
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data.get("error") == "User not found"


def test_get_user_by_id_exception(client, monkeypatch):
    from app.routes import ERROR_MESSAGE

    dummy_user = DummyUser("dummy", "testuser", "test@example.com", "password123")
    # Ensure login_required passes by making current_user the dummy user.
    monkeypatch.setattr("flask_login.utils._get_user", lambda: dummy_user)
    # Override get_user_by_id (called in the view) to raise an exception.
    monkeypatch.setattr(
        "app.routes.get_user_by_id",
        lambda user_id: (_ for _ in ()).throw(RuntimeError("Forced exception")),
    )
    with client.session_transaction() as sess:
        sess["user_id"] = dummy_user.id
        sess["_user_id"] = dummy_user.id
    response = client.get("/users/dummy")
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data.get("error") == ERROR_MESSAGE


def test_get_user_by_id_success(client, monkeypatch):
    # New test: Successful retrieval of a user by ID.
    dummy_user = DummyUser("dummyid", "testuser", "test@example.com", "password123")

    def get_user_by_id(user_id):
        return dummy_user if user_id == dummy_user.id else None

    monkeypatch.setattr("app.routes.get_user_by_id", get_user_by_id)
    with client.session_transaction() as sess:
        sess["user_id"] = dummy_user.id
        sess["_user_id"] = dummy_user.id
    response = client.get(f"/users/{dummy_user.id}")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data.get("id") == dummy_user.id
    assert json_data.get("username") == dummy_user.username
    assert json_data.get("email") == dummy_user.email


# ================= HTML/Form Branch Tests =================


def test_home_renders_index(client, monkeypatch):
    # Simple test to verify index template rendering.
    monkeypatch.setattr(
        "app.routes.render_template", lambda template, **kwargs: f"Rendered {template}"
    )
    response = client.get("/")
    assert response.status_code == 200
    assert b"Rendered index.html" in response.data


def test_dashboard_renders_dashboard(client, monkeypatch):
    dummy_user = DummyUser("dummyid", "testuser", "test@example.com", "password123")
    monkeypatch.setattr(
        "app.routes.get_user_by_id",
        lambda user_id: dummy_user if user_id == dummy_user.id else None,
    )
    monkeypatch.setattr(
        "app.routes.render_template",
        lambda template, **kwargs: f"Rendered {template} for {kwargs.get('user')}",
    )
    with client.session_transaction() as sess:
        sess["user_id"] = dummy_user.id
        sess["_user_id"] = dummy_user.id
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Rendered dashboard.html" in response.data


def test_register_form_renders_html(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.render_template", lambda template: f"Rendered {template}"
    )
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Rendered register.html" in response.data


def test_register_missing_fields_html(client, monkeypatch):
    # HTML branch: missing fields should flash an error message and redirect.
    flashed_messages = []

    def fake_flash(message, category):
        flashed_messages.append((message, category))

    monkeypatch.setattr("app.routes.flash", fake_flash)

    # Simulate HTML form submission with missing 'password'
    data = {"username": "testuser", "email": "test@example.com"}
    response = client.post("/register", data=data)  # Let default content type be used

    # Since required fields are missing, the route flashes "All fields are required."
    assert flashed_messages == [("All fields are required.", "danger")]

    # Verify that the response is a redirect (HTTP 302)
    assert response.status_code == 302

    # Verify that the redirect location is the registration form route.
    from flask import url_for

    expected_location = url_for("main.show_register_form")
    assert expected_location in response.headers.get("Location", "")


def test_register_existing_email_html(client, monkeypatch):
    # HTML branch: email already registered.
    flashed_messages = []

    def fake_flash(message, category):
        flashed_messages.append((message, category))

    monkeypatch.setattr("app.routes.flash", fake_flash)
    # Simulate that the email already exists.
    monkeypatch.setattr("app.routes.get_user_by_email", lambda email: object())
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    }
    response = client.post("/register", data=data)
    # Expect the "Email is already registered." flash message.
    assert ("Email is already registered.", "danger") in flashed_messages
    assert response.status_code == 302
    redirect_location = response.headers.get("Location", "")
    assert "/register" in redirect_location


def test_register_success_html(client, monkeypatch):
    # HTML branch: successful registration flashes success and redirects.
    flashed_messages = []

    def fake_flash(message, category):
        flashed_messages.append((message, category))

    monkeypatch.setattr("app.routes.flash", fake_flash)
    monkeypatch.setattr("app.routes.get_user_by_email", lambda email: None)
    fake_user_id = "fakeid123"
    monkeypatch.setattr("app.routes.create_user", lambda user_data: fake_user_id)
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    }
    response = client.post(
        "/register", data=data, content_type="application/x-www-form-urlencoded"
    )
    assert ("Registration successful!", "success") in flashed_messages
    assert response.status_code == 302
    redirect_location = response.headers.get("Location", "")
    assert "/login" in redirect_location


def test_register_exception_html(client, monkeypatch):
    # HTML branch: exception in registration flashes error and redirects.
    flashed_messages = []

    def fake_flash(message, category):
        flashed_messages.append((message, category))

    monkeypatch.setattr("app.routes.flash", fake_flash)
    monkeypatch.setattr("app.routes.get_user_by_email", lambda email: None)

    def raise_exception(user_data):
        raise RuntimeError("Forced exception")

    monkeypatch.setattr("app.routes.create_user", raise_exception)
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    }
    response = client.post("/register", data=data)
    assert ("An error occurred. Please try again.", "danger") in flashed_messages
    assert response.status_code == 302
    redirect_location = response.headers.get("Location", "")
    assert "/register" in redirect_location


def test_login_form_renders_html(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.render_template", lambda template: f"Rendered {template}"
    )
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Rendered login.html" in response.data


def test_login_success_html(client, monkeypatch):
    # HTML branch: successful login.
    flashed_messages = []

    def fake_flash(message, category):
        flashed_messages.append((message, category))

    monkeypatch.setattr("app.routes.flash", fake_flash)
    data = {"email": "test@example.com", "password": "password123"}
    dummy_user = DummyUser("dummyid", "testuser", "test@example.com", "password123")
    monkeypatch.setattr(
        "app.routes.get_user_by_email",
        lambda email: dummy_user if email == data["email"] else None,
    )
    response = client.post("/login", data=data)
    # Expect a flash message and a redirect to dashboard.
    assert ("Login successful!", "success") in flashed_messages
    assert response.status_code == 302
    redirect_location = response.headers.get("Location", "")
    assert "/dashboard" in redirect_location


def test_login_failure_html(client, monkeypatch):
    # HTML branch: login failure flashes error and redirects.
    flashed_messages = []

    def fake_flash(message, category):
        flashed_messages.append((message, category))

    monkeypatch.setattr("app.routes.flash", fake_flash)
    data = {"email": "test@example.com", "password": "wrongpassword"}
    dummy_user = DummyUser("dummyid", "testuser", "test@example.com", "password123")
    monkeypatch.setattr(
        "app.routes.get_user_by_email",
        lambda email: dummy_user if email == data["email"] else None,
    )
    response = client.post("/login", data=data)
    assert ("Invalid email or password.", "danger") in flashed_messages
    assert response.status_code == 302
    # Verify that redirect location is "/login"
    redirect_location = response.headers.get("Location", "")
    assert redirect_location == "/login"


def test_login_exception_html(client, monkeypatch):
    # HTML branch: exception in login (HTML) flashes error and redirects.
    from flask import url_for

    from app.routes import ERROR_TRY_AGAIN

    flashed_messages = []

    def fake_flash(message, category):
        flashed_messages.append((message, category))

    monkeypatch.setattr("app.routes.flash", fake_flash)
    # Force an exception by dividing by zero.
    monkeypatch.setattr("app.routes.get_user_by_email", lambda email: 1 / 0)
    data = {"email": "test@example.com", "password": "password123"}
    response = client.post("/login", data=data)
    assert (ERROR_TRY_AGAIN, "danger") in flashed_messages
    assert response.status_code == 302
    expected_redirect = url_for("main.show_login_form")
    redirect_location = response.headers.get("Location", "")
    assert expected_redirect == redirect_location


def test_get_users_success_json(client, monkeypatch):
    # Test the GET branch of /users.
    # Create a fake users collection with one dummy document.
    dummy_doc = {
        "_id": "user1",
        "username": "user1",
        "email": "user1@example.com",
    }

    class FakeUsersCollection:
        def find(self):
            return [dummy_doc]

    fake_db = type("FakeDB", (), {"users": FakeUsersCollection()})()
    monkeypatch.setattr("app.routes.mongo.db", fake_db)
    # Ensure the request is authenticated.
    dummy_user = DummyUser("dummyid", "testuser", "test@example.com", "password123")
    monkeypatch.setattr("flask_login.utils._get_user", lambda: dummy_user)
    with client.session_transaction() as sess:
        sess["user_id"] = dummy_user.id
        sess["_user_id"] = dummy_user.id
    response = client.get("/users")
    assert response.status_code == 200
    json_data = response.get_json()
    # The view builds a list of dicts with id, username, and email.
    expected = [{"id": "user1", "username": "user1", "email": "user1@example.com"}]
    assert json_data == expected


def test_create_user_success_json(client, monkeypatch):
    # Test the POST branch of /users (successful creation).
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword",
    }
    # Ensure the request is authenticated.
    dummy_user = DummyUser("dummyid", "testuser", "test@example.com", "password123")
    monkeypatch.setattr("flask_login.utils._get_user", lambda: dummy_user)
    with client.session_transaction() as sess:
        sess["user_id"] = dummy_user.id
        sess["_user_id"] = dummy_user.id

    # Create a fake insert result with an inserted_id attribute.
    class FakeInsertResult:
        inserted_id = "newuser1"

    # Create a fake users collection with an insert_one method.
    class FakeUsersCollection:
        def insert_one(self, data):
            # Ensure the password is hashed and does not match the raw password.
            assert data["password"] != "newpassword"
            return FakeInsertResult()

    fake_db = type("FakeDB", (), {"users": FakeUsersCollection()})()
    monkeypatch.setattr("app.routes.mongo.db", fake_db)
    response = client.post("/users", json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data.get("user_id") == "newuser1"


def test_users_method_not_allowed(client):
    # Test that an unsupported HTTP method (e.g. PUT) on /users returns 405.
    response = client.put("/users")
    assert response.status_code == 405


def test_create_user_exception_json_alternate(client, monkeypatch):
    # Alternate test for the exception branch in POST /users.
    from app.routes import ERROR_MESSAGE

    # Create a fake users collection that raises an exception.
    class FakeUsersCollection:
        def insert_one(self, data):
            raise RuntimeError("Forced exception")

    fake_db = type("FakeDB", (), {"users": FakeUsersCollection()})()
    monkeypatch.setattr("app.routes.mongo.db", fake_db)
    dummy_user = DummyUser("dummyid", "testuser", "test@example.com", "password123")
    # Ensure the user is considered authenticated.
    monkeypatch.setattr("flask_login.utils._get_user", lambda: dummy_user)
    with client.session_transaction() as sess:
        sess["user_id"] = dummy_user.id
        sess["_user_id"] = dummy_user.id

    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword",
    }
    response = client.post("/users", json=data)
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data.get("error") == ERROR_MESSAGE


def test_users_post_branch_directly(client, monkeypatch):
    # Directly test the POST branch of the /users endpoint.
    from app.routes import users

    # Prepare a fake POST request with JSON data.
    test_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword",
    }

    # Create a fake insert result with an inserted_id attribute.
    class FakeInsertResult:
        inserted_id = "newid"

    # Create a fake users collection with a working insert_one method.
    class FakeUsersCollection:
        def insert_one(self, data):
            # Ensure the password has been hashed.
            assert data["password"] != test_data["password"]
            return FakeInsertResult()

    fake_db = type("FakeDB", (), {"users": FakeUsersCollection()})()
    monkeypatch.setattr("app.routes.mongo.db", fake_db)

    # We need to simulate an authenticated user for login_required.
    dummy_user = DummyUser("dummyid", "testuser", "test@example.com", "password123")
    monkeypatch.setattr("flask_login.utils._get_user", lambda: dummy_user)
    with client.application.test_request_context(
        "/users", method="POST", json=test_data
    ):
        # Directly call the view function.
        response = users()
        # The view returns a tuple: (jsonify(response_body), status_code)
        # We expect a 201 status code.
        assert response[1] == 201
        json_data = response[0].get_json()
        assert json_data.get("user_id") == "newid"
