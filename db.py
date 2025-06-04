import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")

# Establish a secure MongoDB connection
client = AsyncIOMotorClient(MONGO_DB_URL, tls=True, tlsAllowInvalidCertificates=True)
database = client["translation_data"]

# Collections
translations_collection = database["translations"]
users_collection = database["users"]
pending_translations_collection = database["pending_translations"]
