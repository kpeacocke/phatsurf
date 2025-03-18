import mongomock
import pytest

from app.extensions import mongo


def get_mock_db():
    """
    Create and return a new mongomock database instance.
    """
    client = mongomock.MongoClient()
    return client.db


@pytest.fixture(autouse=True)
def mock_mongo(monkeypatch):
    """
    Automatically replace the mongo.db attribute with a mongomock instance
    for isolated testing.
    """
    mock_db = get_mock_db()
    monkeypatch.setattr(mongo, "db", mock_db)
    return mock_db


def test_mongo_connection(mock_mongo):
    """
    Verify that the MongoDB connection is properly mocked.
    """
    # Ensure that the mongo extension's db is not None and matches our mock.
    assert mongo.db is not None
    assert mongo.db == mock_mongo

    # Insert a test document into a collection.
    test_document = {"name": "PhatSurf"}
    result = mongo.db.test_collection.insert_one(test_document)
    assert result.inserted_id is not None

    # Retrieve the inserted document.
    retrieved_document = mongo.db.test_collection.find_one({"name": "PhatSurf"})
    assert retrieved_document is not None
    assert retrieved_document["name"] == "PhatSurf"
