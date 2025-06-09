import os
from writer.data_writer import DataWriter

# Fetch MongoDB configuration from environment variables
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://mongodb:27017')

def test_insert_and_cleanup():
    try:
        writer = DataWriter(MONGODB_URI)
        test_doc = {"sensor_type": "test", "reading": {"value": 123}, "location": {"latitude": 0, "longitude": 0}}
        result = writer.collection.insert_one(test_doc)
        assert result.acknowledged, "Failed to insert the document into MongoDB"
        writer.collection.delete_one({"_id": result.inserted_id})
    except Exception as e:
        assert False, f"Error connecting to or manipulating MongoDB: {e}"

def test_empty_collection():
    try:
        writer = DataWriter(MONGODB_URI)
        # Clear the collection before testing
        writer.collection.delete_many({})
        count = writer.collection.count_documents({})
        assert count == 0, "The collection is not empty"
    except Exception as e:
        assert False, f"Error connecting to or manipulating MongoDB: {e}"

def test_duplicate_insertion():
    try:
        writer = DataWriter(MONGODB_URI)
        test_doc = {"sensor_type": "test", "sensor_id": "duplicate_test", "reading": {"value": 123}, "location": {"latitude": 0, "longitude": 0}}
        
        # Clear the collection before testing
        writer.collection.delete_many({})
        
        # Insert the document once
        writer.collection.insert_one(test_doc)
        
        # Attempt to insert the same document again
        try:
            writer.collection.insert_one(test_doc)
            assert False, "Duplicate document was inserted"
        except Exception as e:
            assert "duplicate key error" in str(e), f"Unexpected error: {e}"
        
        # Clean up
        writer.collection.delete_one({"sensor_id": "duplicate_test"})
    except Exception as e:
        assert False, f"Error connecting to or manipulating MongoDB: {e}"