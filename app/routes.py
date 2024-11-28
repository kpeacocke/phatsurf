from flask import Blueprint, request, jsonify
from app.extensions import mongo

main = Blueprint('main', __name__)

@main.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user in the database.
    """
    data = request.json

    # Validate required fields
    required_fields = ["location", "weight", "fitness"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    # Proceed with creating the user
    user = {
        "location": data["location"],
        "weight": data["weight"],
        "fitness": data["fitness"]
    }
    result = mongo.db.users.insert_one(user)
    return jsonify({"message": "User created", "user_id": str(result.inserted_id)}), 201


@main.route('/users', methods=['GET'])
def get_users():
    """
    Retrieve all users from the database.
    """
    users = mongo.db.users.find()
    user_list = [
        {"id": str(user["_id"]), "location": user["location"], "weight": user["weight"], "fitness": user["fitness"]}
        for user in users
    ]
    return jsonify(user_list), 200
