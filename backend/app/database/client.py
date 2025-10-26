from pymongo import MongoClient
from dotenv import load_dotenv
from loguru import logger
import os

load_dotenv()

class MongoDB:
    def __init__(self):
        self.uri = os.getenv("MONGODB_URI")
        self.client = None
        self.db = None

    def connect(self):
        """Connect to MongoDB and send a ping to verify connection"""
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client["data"]
            # Send ping to verify connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

mongodb = MongoDB()
