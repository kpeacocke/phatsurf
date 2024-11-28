from app.extensions import mongo

def test_mongo_connection(app):
    """
    Test MongoDB connection initialization.
    """
    assert mongo.db is not None
