from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from app.extensions import mongo
from app.models import create_user, get_user_by_email, get_user_by_id

main = Blueprint("main", __name__)
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "main.login"

ERROR_MESSAGE = "An unexpected error occurred"
ERROR_TRY_AGAIN = "An error occurred. Please try again."
REGISTER_FORM_ROUTE = "main.show_register_form"
LOGIN_FORM_ROUTE = "main.show_login_form"


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader function"""
    return get_user_by_id(user_id)


@main.route("/", methods=["GET"])
def home():
    """Render the homepage"""
    return render_template("index.html")


@main.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """Render the user dashboard"""
    return render_template("dashboard.html", user=current_user)


# ✅ Fix: Add GET route for Registration Page
@main.route("/register", methods=["GET"])
def show_register_form():
    """Render the registration form page."""
    return render_template("register.html")


@main.route("/register", methods=["POST"])
def register():
    """Register a new user"""
    try:
        data = (
            request.get_json(silent=True) or request.form
        )  # Handle both JSON and form data
        required_fields = ["username", "email", "password"]
        if not all(field in data and data[field] for field in required_fields):
            if request.is_json:
                return jsonify({"error": "All fields are required."}), 400
            flash("All fields are required.", "danger")
            return redirect(url_for(REGISTER_FORM_ROUTE))
        if get_user_by_email(data["email"]):
            if request.is_json:
                return jsonify({"error": "Email is already registered."}), 400
            flash("Email is already registered.", "danger")
            return redirect(url_for(REGISTER_FORM_ROUTE))
        hashed_bytes = bcrypt.generate_password_hash(data["password"])
        hashed_password = hashed_bytes.decode("utf-8")

        user_data = {
            "username": data["username"],
            "email": data["email"],
            "password": hashed_password,
        }
        # Capture the user id (e.g., for JSON response)
        user_id = create_user(user_data)
        if request.is_json:
            return jsonify({"message": "User registered", "user_id": user_id}), 201
        flash("Registration successful!", "success")
        return redirect(url_for("main.login"))
    except Exception as e:
        current_app.logger.error(f"Error in register: {e}")
        if request.is_json:
            return jsonify({"error": ERROR_TRY_AGAIN}), 500
        flash("An error occurred. Please try again.", "danger")
        return redirect(url_for(REGISTER_FORM_ROUTE))


@main.route("/login", methods=["GET"])
def show_login_form():
    """Render the login form page."""
    return render_template("login.html")


@main.route("/login", methods=["POST"])
def login():
    """User login"""
    try:
        if request.is_json:
            data = request.get_json()
            user = get_user_by_email(data.get("email"))
            if not user or not user.check_password(data.get("password")):
                return jsonify({"error": "Invalid email or password."}), 401
            login_user(user)
            session["user_id"] = user.id
            return jsonify({"message": "Login successful", "user_id": user.id}), 200
        else:
            data = request.form
            user = get_user_by_email(data.get("email"))
            if not user or not user.check_password(data.get("password")):
                flash("Invalid email or password.", "danger")
                return redirect(url_for(LOGIN_FORM_ROUTE))
            login_user(user)
            session["user_id"] = user.id
            flash("Login successful!", "success")
            return redirect(url_for("main.dashboard"))
    except Exception as e:
        current_app.logger.error(f"Error in login: {e}")
        if request.is_json:
            return jsonify({"error": ERROR_TRY_AGAIN}), 500
        flash(ERROR_TRY_AGAIN, "danger")
        return redirect(url_for(LOGIN_FORM_ROUTE))


@main.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout user and return JSON response."""
    logout_user()
    session.pop("user_id", None)
    session.pop("_user_id", None)
    return jsonify({"message": "Logout successful"}), 200


@main.route("/profile", methods=["GET"])
@login_required
def profile():
    """Get the logged-in user's profile"""
    try:
        user = get_user_by_id(current_user.id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        return (
            jsonify({"id": user.id, "username": user.username, "email": user.email}),
            200,
        )
    except RuntimeError as e:  # Catching a more specific exception
        current_app.logger.error(f"Error in profile: {e}")
        return jsonify({"error": ERROR_MESSAGE}), 500


@main.route("/users", methods=["GET", "POST"])
@login_required
def users():
    """Retrieve all users (GET) or create a new user (POST)"""
    if request.method == "GET":
        try:
            users_cursor = mongo.db.users.find()
            user_list = [
                {
                    "id": str(user["_id"]),
                    "username": user["username"],
                    "email": user["email"],
                }
                for user in users_cursor
            ]
            return jsonify(user_list), 200
        except Exception as e:
            current_app.logger.error(f"Error in get_users: {e}")
            return jsonify({"error": ERROR_MESSAGE}), 500
    else:  # POST
        try:
            data = request.get_json()  # You might consider using silent=True if needed.
            required_keys = ["username", "email", "password"]
            if not data or not all(k in data for k in required_keys):
                return jsonify({"error": "Missing required fields"}), 400

            hashed_bytes = bcrypt.generate_password_hash(data["password"])
            hashed_password = hashed_bytes.decode("utf-8")
            user_id = mongo.db.users.insert_one(
                {
                    "username": data["username"],
                    "email": data["email"],
                    "password": hashed_password,
                }
            ).inserted_id

            return jsonify({"user_id": str(user_id)}), 201
        except Exception as e:
            current_app.logger.error(f"Error in create_user: {e}")
            return jsonify({"error": ERROR_MESSAGE}), 500


@main.route("/users/<user_id>", methods=["GET"])
@login_required
def get_user_by_id_route(user_id):
    """Retrieve a user by ID"""
    try:
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        return (
            jsonify({"id": user.id, "username": user.username, "email": user.email}),
            200,
        )
    except Exception as e:
        current_app.logger.error(f"Error in get_user_by_id: {e}")
        return jsonify({"error": ERROR_MESSAGE}), 500


@main.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200
