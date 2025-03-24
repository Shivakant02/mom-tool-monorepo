
import os
import requests
import json
import re
import html
import pytz
from datetime import datetime
from fuzzywuzzy import process  # pip install fuzzywuzzy
from urllib.parse import quote
from pymongo import MongoClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

load_dotenv()  # Loads environment variables from .env

app = FastAPI()

# Debug: check that environment variables are loaded
DB_URL = os.getenv("DB_URL")
GRAPH_ACCESS_TOKEN = os.getenv("GRAPH_ACCESS_TOKEN")
if not DB_URL:
    raise Exception("DB_URL is not set in the environment variables.")
if not GRAPH_ACCESS_TOKEN:
    raise Exception("GRAPH_ACCESS_TOKEN is not set in the environment variables.")

# MongoDB connection
client = MongoClient(DB_URL)
db = client["meeting_db"]
meeting_records = db.meeting_records


def get_latest_meeting_info(access_token):
    """
    Retrieves the meeting address, chat ID, and event details for the latest past online meeting.
    """
    now = datetime.utcnow().isoformat() + 'Z'
    events_url = "https://graph.microsoft.com/v1.0/me/events"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(events_url, headers=headers)
    response.raise_for_status()
    data = response.json()
    events = data.get("value", [])
    if not events:
        raise Exception("No past online meetings found.")
    latest_event = events[0]
    join_url = latest_event.get("onlineMeeting", {}).get("joinUrl")
    if not join_url:
        raise Exception("No joinUrl found for the latest meeting.")
    # Extract the meeting address from the joinUrl
    match = re.search(r"l/meetup-join/([^/]+)/", join_url)
    if match:
        meeting_add = match.group(1)
    else:
        raise Exception("Unable to extract meeting address from joinUrl")
    meeting_id = meeting_add
    chat_id = meeting_add
    return meeting_id, chat_id, latest_event


def extract_attendees(event):
    """
    Extracts the attendees' names and emails from the event data.
    """
    attendees = event.get("attendees", [])
    result = []
    for attendee in attendees:
        email_info = attendee.get("emailAddress", {})
        name = email_info.get("name")
        email = email_info.get("address")
        if name and email:
            result.append({"name": name, "email": email})
    return result


def extract_teams_chat_messages(access_token, chat_id):
    """
    Extracts chat messages from a Microsoft Teams chat.
    """
    url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
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
        return messages

    except Exception as err:
        print(f"Error extracting chat messages: {err}")
        return []


def save_to_text_file(messages, output_file="teams_chat_export.txt"):
    """
    Saves the extracted messages to a text file.
    """
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("Time | Sender | Message\n")
            f.write("-" * 100 + "\n")
            for msg in messages:
                f.write(f"{msg['formatted_time']} | {msg['sender']} | {msg['content']}\n\n")
        print(f"Chat messages successfully exported to {output_file}")
    except Exception as e:
        print(f"Error saving to file: {e}")


def list_transcripts(access_token, meeting_id):
    """
    Lists available transcripts for a given online meeting.
    """
    url = f"https://graph.microsoft.com/v1.0/me/onlineMeetings/{meeting_id}/transcripts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data.get("value", [])


def download_transcript_content(access_token, content_url):
    """
    Downloads the content of a transcript.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(content_url, headers=headers)
    response.raise_for_status()
    return response.content


def process_transcript(filename, attendees):
    """
    Hits the processing API and then applies fuzzy matching to correct action item owner names
    using the extracted attendees list.
    """
    api_url = f"http://localhost:8001/process?filename={filename}"
    response_AI = requests.get(api_url)
    response_AI.raise_for_status()
    data = response_AI.json()

    transcript = data.get("transcript")
    extracted_info_str = data.get("extracted_info")
    try:
        extracted_info = json.loads(extracted_info_str)
    except Exception:
        extracted_info = extracted_info_str
    action_items = extracted_info.get("action_items", [])
    original_names = [item.get("owner") for item in action_items]
    attendee_names = [att["name"] for att in attendees]

    # Hit the matching API to correct names
    url = "http://localhost:8000/match"
    payload = {
        "names_list": original_names,
        "attendees_list": attendee_names
    }
    response_Match = requests.post(url, json=payload)
    result_json = response_Match.json()
    result_str = result_json.get("result")

    # Extract JSON content from backticks if present
    match_res = re.search(r"```json\n(.*?)\n```", result_str, re.DOTALL)
    if match_res:
        json_content = match_res.group(1)
        try:
            matches_list = json.loads(json_content)
        except Exception as e:
            print("Error parsing JSON from match result:", e)
            matches_list = []
    else:
        matches_list = []

    # Update the action items with corrected owner names
    for match_item in matches_list:
        original_name = match_item.get("Original_Name")
        matched_attendee = match_item.get("Matched_Attendee")
        if matched_attendee != "Unmatched":
            for item in action_items:
                if item.get("owner") == original_name:
                    attendee_detail = next((att for att in attendees if att["name"] == matched_attendee), None)
                    if attendee_detail:
                        print(
                            f"Correcting owner: {original_name} -> {matched_attendee} with email {attendee_detail.get('email')}")
                        item["owner"] = matched_attendee
                        item["email"] = attendee_detail.get("email")
                    else:
                        print(f"Correcting owner: {original_name} -> {matched_attendee} (no email found)")
                        item["owner"] = matched_attendee
    return action_items, extracted_info


@app.get("/process_meeting")
def process_meeting():
    """
    Processes the latest meeting by retrieving meeting and chat details,
    processing the transcript, and returning the MOM data.
    """
    access_token = os.getenv("GRAPH_ACCESS_TOKEN")
    try:
        meeting_id, chat_id, event = get_latest_meeting_info(access_token)
        meeting_subject = event.get('subject', 'Unnamed Meeting')
        print(f"Processing meeting: {meeting_subject} {meeting_id}")

        # Check for existing meeting record in MongoDB
        existing_record = meeting_records.find_one({"meeting_id": meeting_id})
        if existing_record:
            print("Found cached meeting data in MongoDB")
            return {
                "mom_data": existing_record["mom_data"]
            }

        attendees = extract_attendees(event)

        # Extract Teams chat messages and save them to file
        messages = extract_teams_chat_messages(access_token, chat_id)
        if messages:
            start_time = event["start"]["dateTime"]
            start_time_str = datetime.fromisoformat(start_time.replace('Z', '+00:00')).strftime("%Y%m%d_%H%M%S")
            chat_filename = f"chat_{start_time_str}.txt"
            save_to_text_file(messages, chat_filename)
        else:
            print("No chat messages found.")

        # Process transcripts if available (commented out for now)
        # transcripts = list_transcripts(access_token, meeting_id)
        # if transcripts:
        #     for transcript_meta in transcripts:
        #         transcript_id = transcript_meta["id"]
        #         content_url = transcript_meta["contentUrl"]
        #         content = download_transcript_content(access_token, content_url)
        #         transcript_filename = f"transcript_{transcript_id}_{start_time_str}.vtt"
        #         with open(transcript_filename, "wb") as f:
        #             f.write(content)
        #         print(f"Transcript saved to {transcript_filename}")
        # else:
        #     print("No transcripts found for this meeting.")

        # Process transcript using the processing API and apply fuzzy matching
        final_items, mom_data = process_transcript("MOMTesting.vtt", attendees)

        meeting_record = {
            "meeting_id": meeting_id,
            "meeting_subject": meeting_subject,
            "meeting_time": datetime.fromisoformat(event["start"]["dateTime"].replace('Z', '+00:00')),
            "attendees": attendees,
            "mom_data": mom_data,
            "processed_at": datetime.now()
        }
        result_insert = meeting_records.insert_one(meeting_record)
        print(f"Stored meeting data in MongoDB with ID: {result_insert.inserted_id}")

        return {"mom_data": mom_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class UpdateMOMRequest(BaseModel):
    meeting_id: str
    mom_data: dict


@app.put("/update_mom")
def update_mom(data: UpdateMOMRequest):
    """
    Updates the mom_data for a given meeting record.
    """
    result = meeting_records.update_one(
        {"meeting_id": data.meeting_id},
        {"$set": {"mom_data": data.mom_data, "updated_at": datetime.now()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Meeting record not found or no update performed.")
    # Return the updated record
    updated_record = meeting_records.find_one({"meeting_id": data.meeting_id})
    return {"updated_record": updated_record}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)




