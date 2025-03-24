import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB URL from environment variables
DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise Exception("DB_URL is not set in the environment variables.")

# Initialize MongoDB connection
client = MongoClient(DB_URL)
db = client["meeting_db"]
meeting_records = db["meeting_records"]

