from fastapi import APIRouter, HTTPException
import requests
import os
import pytz
import html
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
GRAPH_ACCESS_TOKEN = os.getenv("GRAPH_ACCESS_TOKEN")

teams_router = APIRouter()

@teams_router.get("/teams_chat/{chat_id}")
def extract_teams_chat_messages(chat_id: str):
    """Extracts chat messages from a Microsoft Teams chat."""
    # (Include your existing Teams chat extraction logic here)
    return {"message": "Teams chat extracted"}
