import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "speak_check")

# Use short timeouts to avoid UI freezing if Mongo is unavailable
_client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=1000,
    connectTimeoutMS=1000,
    socketTimeoutMS=1000,
)

db = _client[MONGODB_DB]
