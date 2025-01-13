from bson import ObjectId
from flask import Blueprint, current_app, jsonify, request

from app.extensions import mongo

main = Blueprint("main", __name__)

ERROR_MESSAGE = "An unexpected error occurred"


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
    try:
        float(data["weight"])
    except ValueError:
        return False, "could not convert string to float"

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
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Request body is empty"}), 400

        is_valid, error_message = validate_user_data(data)
        if not is_valid:
            return jsonify({"error": error_message}), 400

        user = {
            "location": data["location"],
            "weight": float(data["weight"]),
            "fitness": data["fitness"],
        }
        result = mongo.db.users.insert_one(user)
        return (
            jsonify({"message": "User created", "user_id": str(result.inserted_id)}),
            201,
        )
    except Exception as e:
        current_app.logger.error(f"Error in create_user: {e}")
        return jsonify({"error": ERROR_MESSAGE}), 500


@main.route("/users", methods=["GET"])
def get_users():
    """
    Retrieve all users from the database.
    """
    try:
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
    except Exception as e:
        current_app.logger.error(f"Error in get_users: {e}")
        return jsonify({"error": ERROR_MESSAGE}), 500


@main.route("/users/<user_id>", methods=["GET"])
def get_user_by_id(user_id):
    """
    Retrieve a single user by ID.
    """
    try:
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_data = {
            "id": str(user["_id"]),
            "location": user["location"],
            "weight": user["weight"],
            "fitness": user["fitness"],
        }
        return jsonify(user_data), 200
    except Exception as e:
        current_app.logger.error(f"Error in get_user_by_id: {e}")
        return jsonify({"error": ERROR_MESSAGE}), 500


@main.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    """
    return jsonify({"status": "healthy"}), 200
