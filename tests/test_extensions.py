import mongomock
import pytest

from app.extensions import mongo


@pytest.fixture(scope="function", autouse=True)
def mock_mongo_instance():
    """
    Replace MongoDB with a mongomock instance for isolated testing.
    """
    mock_db = mongomock.MongoClient().db
    mongo.db = mock_db  # Inject the mocked database into the `mongo` extension
    return mock_db


def test_mongo_connection(mock_mongo_instance):
    """
    Test MongoDB connection initialization.
    """
    assert mongo.db is not None
    assert mongo.db == mock_mongo_instance

    # Test inserting and retrieving a document
    test_document = {"name": "PhatSurf"}
    result = mongo.db.test_collection.insert_one(test_document)
    assert result.inserted_id is not None

    retrieved_document = mongo.db.test_collection.find_one({"name": "PhatSurf"})
    assert retrieved_document is not None
    assert retrieved_document["name"] == "PhatSurf"
