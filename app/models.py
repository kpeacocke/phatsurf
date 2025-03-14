from bson import ObjectId
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import mongo


class User(UserMixin):
    """
    User model for authentication.
    """

    def __init__(
        self,
        user_id,
        username,
        email,
        password_hash,
        location=None,
        weight=None,
        fitness=None,
    ):
        self.id = str(user_id)  # Flask-Login requires a string ID
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.location = location
        self.weight = weight
        self.fitness = fitness

    def check_password(self, password):
        """
        Check if the provided password matches the hashed password.
        """
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def from_mongo(user_data):
        """
        Convert MongoDB document into a User object.
        """
        if not user_data:
            return None
        return User(
            user_id=user_data["_id"],
            username=user_data["username"],
            email=user_data["email"],
            password_hash=user_data["password"],
            location=user_data.get("location"),
            weight=user_data.get("weight"),
            fitness=user_data.get("fitness"),
        )


def get_users():
    """
    Retrieve all users from the MongoDB collection.
    """
    users = mongo.db.users.find()
    return [
        {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "location": user.get("location"),
            "weight": user.get("weight"),
            "fitness": user.get("fitness"),
        }
        for user in users
    ]


def create_user(data):
    """
    Add a new user to the MongoDB collection with hashed password.
    """
    if "password" in data:
        data["password"] = generate_password_hash(data["password"])
    result = mongo.db.users.insert_one(data)
    return str(result.inserted_id)


def get_user_by_id(user_id):
    """
    Retrieve a single user by their MongoDB ObjectId.
    """
    try:
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        return User.from_mongo(user)
    except Exception:
        return None


def get_user_by_email(email):
    """
    Retrieve a single user by email.
    """
    try:
        user = mongo.db.users.find_one({"email": email})
        return User.from_mongo(user)
    except Exception:
        return None
