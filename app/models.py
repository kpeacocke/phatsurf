from app.extensions import mongo


def get_users():
    """
    Retrieve all users from the MongoDB collection.
    """
    return list(mongo.db.users.find())


def create_user(data):
    """
    Add a new user to the MongoDB collection.
    """
    return mongo.db.users.insert_one(data)
