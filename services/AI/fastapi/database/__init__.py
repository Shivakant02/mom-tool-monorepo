import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise Exception("DB_URL is not set in the environment variables.")

client = MongoClient(DB_URL)
db = client["meeting_db"]
meeting_records = db.meeting_records
