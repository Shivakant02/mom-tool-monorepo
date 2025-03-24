import requests
import re
import html
import pytz
from datetime import datetime
from fastapi import APIRouter, HTTPException
import os
from dotenv import load_dotenv

load_dotenv()
GRAPH_ACCESS_TOKEN = os.getenv("GRAPH_ACCESS_TOKEN")

teams_router = APIRouter()

@teams_router.get("/teams_chat/{chat_id}")
def extract_teams_chat_messages(chat_id: str):
    """
    Extracts chat messages from a Microsoft Teams chat.
    """
    url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages"
    headers = {
        "Authorization": f"Bearer {GRAPH_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    messages = []
    try:
        while url:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            for msg in data.get("value", []):
                if not msg.get("from") or not msg.get("from").get("user"):
                    continue

                timestamp = msg.get("createdDateTime")
                dt_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                ist_timezone = pytz.timezone('Asia/Kolkata')
                ist_time = dt_obj.astimezone(ist_timezone)

                sender = msg.get("from", {}).get("user", {}).get("displayName", "Unknown User")
                content = msg.get("body", {}).get("content", "")
                content = re.sub(r'<[^>]*>', ' ', content)
                content = html.unescape(content)
                content = re.sub(r'\s+', ' ', content).strip()

                messages.append({
                    "timestamp": ist_time,
                    "formatted_time": ist_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "sender": sender,
                    "content": content
                })

            url = data.get("@odata.nextLink")

        messages.sort(key=lambda x: x["timestamp"])
        return {"messages": messages}

    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Error extracting chat messages: {err}")
