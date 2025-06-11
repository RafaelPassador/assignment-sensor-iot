from pymongo import MongoClient
import logging
from writer.database import DatabaseWriter

class DataWriter(DatabaseWriter):
    def __init__(self, mongodb_uri="mongodb://mongodb:27017"):
        self.mongodb_uri = mongodb_uri
        self.client = None
        self.db = None
        self.collection = None
        self.connect()

    def connect(self):
        """Establish connection to MongoDB."""
        try:
            self.client = MongoClient(self.mongodb_uri, serverSelectionTimeoutMS=3000)
            self.db = self.client["iot"]
            self.collection = self.db["sensores"]
            self.client.server_info()
            logging.info(" Connected to MongoDB")

            # Check if the collection already has data
            if self.collection.count_documents({}) > 0:
                logging.info(" Database already contains data. Continuing to add new data.")
            else:
                logging.info(" Database is empty. Starting fresh.")
        except Exception as e:
            logging.error(f" Failed to connect to MongoDB: {e}")
            raise

    def process(self, data):
        """Process and store data in MongoDB."""
        if not isinstance(data, dict):
            logging.warning(f"Ignored non-dict data: {data}")
            return
        try:
            # Check for duplicates based on sensor_id
            if self.collection.find_one({"sensor_id": data["sensor_id"]}):
                logging.info(f"Duplicate data ignored: {data}")
                return

            self.collection.insert_one(data)
            logging.info(f" Inserted into MongoDB: {data}")
        except Exception as e:
            logging.error(f" Error inserting data: {e}")

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logging.info("MongoDB connection closed.")