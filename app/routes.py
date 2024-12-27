from flask import Blueprint, jsonify, request

from app.extensions import mongo

main = Blueprint("main", __name__)


def validate_user_data(data):
    """
    Validate user input data and check for missing fields.
    """
    required_fields = ["location", "weight", "fitness"]
    missing_fields = [
        field for field in required_fields if field not in data or not data[field]
    ]

    if missing_fields:
        return False, f"Missing or empty fields: {', '.join(missing_fields)}"
    return True, None


@main.route("/", methods=["GET"])
def home():
    """
    Route for the root URL.
    """
    return jsonify({"message": "Welcome to PhatSurf!"}), 200


@main.route("/users", methods=["POST"])
def create_user():
    """
    Create a new user in the database.
    """
    data = request.json

    if not data:
        return jsonify({"error": "Request body is empty"}), 400

    # Validate user data
    is_valid, error_message = validate_user_data(data)
    if not is_valid:
        return jsonify({"error": error_message}), 400

    # Create user in the database
    user = {
        "location": data["location"],
        "weight": data["weight"],
        "fitness": data["fitness"],
    }
    result = mongo.db.users.insert_one(user)
    return jsonify({"message": "User created", "user_id": str(result.inserted_id)}), 201


@main.route("/users", methods=["GET"])
def get_users():
    """
    Retrieve all users from the database.
    """
    users = mongo.db.users.find()
    user_list = [
        {
            "id": str(user["_id"]),
            "location": user["location"],
            "weight": user["weight"],
            "fitness": user["fitness"],
        }
        for user in users
    ]
    return jsonify(user_list), 200


@main.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    """
    return jsonify({"status": "healthy"}), 200
