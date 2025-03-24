import os
import base64
import requests
import threading
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import convertapi

load_dotenv()

# MongoDB Connection
client = MongoClient(os.getenv("DB_URL"))
db = client["meeting_db"]
meeting_records = db["meeting_records"]

# Graph API Configuration
GRAPH_ACCESS_TOKEN = os.getenv("GRAPH_ACCESS_TOKEN")
GRAPH_SENDMAIL_ENDPOINT = "https://graph.microsoft.com/v1.0/me/microsoft.graph.sendMail"

# ConvertAPI Key for File Conversion
convertapi.api_secret = os.getenv("Convert_API")

# FastAPI Router
mail_router = APIRouter()

# Pydantic Models
class Attendee(BaseModel):
    name: str
    email: str

class SendMOMRequest(BaseModel):
    meeting_id: str
    attendees: List[Attendee]


def format_mom_content(mom_data: dict) -> str:
    """
    Converts the MOM data into a well-structured human-readable format.
    """
    lines = ["MINUTES OF MEETING", "=" * 50, ""]

    organizer = mom_data.get("organizer", "N/A")
    lines.append(f"Organizer: {organizer}\n")

    lines.append("Discussion Topics:")
    for topic in mom_data.get("discussion_topics", []):
        lines.append(f"  - {topic}")
    lines.append("")

    lines.append("Key Points:")
    for point in mom_data.get("key_points", []):
        lines.append(f"  - {point}")
    lines.append("")

    lines.append("FAQs:")
    for faq in mom_data.get("faqs", []):
        lines.append(f"  - {faq}")
    lines.append("")

    lines.append("Action Items:")
    action_items = mom_data.get("action_items", [])
    for idx, item in enumerate(action_items, start=1):
        lines.append(f"{idx}. {item.get('item', 'N/A')}")
        deadline = item.get("deadline", "N/A")
        owner = item.get("owner", "N/A")
        email = item.get("email", None)
        lines.append(f"    Deadline: {deadline}")
        if email:
            lines.append(f"    Owner: {owner} (Email: {email})")
        else:
            lines.append(f"    Owner: {owner}")
        lines.append("")

    return "\n".join(lines)


def generate_mom_files(meeting_id: str, content: str) -> dict:
    """
    Converts MOM content into PDF, DOCX, and HTML formats using ConvertAPI.
    """
    filenames = {}

    # Generate HTML File
    html_filename = f"mom_{meeting_id}.html"
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(f"<html><body><pre style='font-family: monospace;'>{content}</pre></body></html>")
    filenames["html"] = html_filename

    # Convert HTML to PDF
    pdf_filename = f"mom_{meeting_id}.pdf"
    try:
        result_pdf = convertapi.convert('pdf', {'File': html_filename}, from_format='html')
        result_pdf.file.save(pdf_filename)
        filenames["pdf"] = pdf_filename
    except Exception as e:
        print(f"Error converting HTML to PDF: {e}")

    # Convert HTML to DOCX
    docx_filename = f"mom_{meeting_id}.docx"
    try:
        result_docx = convertapi.convert('docx', {'File': html_filename}, from_format='html')
        result_docx.file.save(docx_filename)
        filenames["docx"] = docx_filename
    except Exception as e:
        print(f"Error converting HTML to DOCX: {e}")

    return filenames


def send_email_with_attachments(attendees: List[Attendee], subject: str, body: str, files: dict):
    """
    Sends an email with MOM files as attachments using Microsoft Graph API.
    """
    to_recipients = [{"emailAddress": {"address": att.email}} for att in attendees]
    attachments = []

    for filetype, filepath in files.items():
        try:
            with open(filepath, "rb") as f:
                file_content = f.read()
            attachment = {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": os.path.basename(filepath),
                "contentBytes": base64.b64encode(file_content).decode("utf-8")
            }
            attachments.append(attachment)
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")

    email_payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "Text", "content": body},
            "toRecipients": to_recipients,
            "attachments": attachments
        },
        "saveToSentItems": "true"
    }

    headers = {
        "Authorization": f"Bearer {GRAPH_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(GRAPH_SENDMAIL_ENDPOINT, headers=headers, json=email_payload)
    if response.status_code not in (200, 202):
        raise Exception(f"Graph API sendMail failed: {response.status_code} - {response.text}")
    print("Email sent successfully.")


def upload_file_to_onedrive(filepath: str, folder: str = "MOMFiles"):
    """
    Uploads MOM files to OneDrive via Microsoft Graph API.
    """
    filename = os.path.basename(filepath)
    upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder}/{filename}:/content"

    try:
        with open(filepath, "rb") as f:
            file_content = f.read()
        headers = {
            "Authorization": f"Bearer {GRAPH_ACCESS_TOKEN}",
            "Content-Type": "application/octet-stream"
        }
        response = requests.put(upload_url, headers=headers, data=file_content)
        if response.status_code in (200, 201):
            print(f"Uploaded {filename} to OneDrive.")
        else:
            print(f"Failed to upload {filename}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error uploading {filename}: {e}")


def upload_all_files_to_onedrive(files: dict):
    """
    Uploads all MOM files to OneDrive.
    """
    for filepath in files.values():
        upload_file_to_onedrive(filepath)


def process_and_send_mom(meeting_id: str, attendees: List[Attendee]):
    """
    Retrieves MOM data from MongoDB, converts it into files, sends email, and uploads to OneDrive.
    """
    try:
        mom_record = meeting_records.find_one({"meeting_id": meeting_id})
        if not mom_record:
            print(f"MOM record not found for meeting_id: {meeting_id}")
            return

        mom_data_obj = mom_record.get("mom_data", {})
        if not mom_data_obj:
            print(f"MOM content is empty for meeting_id: {meeting_id}")
            return

        content = format_mom_content(mom_data_obj)
        files = generate_mom_files(meeting_id, content)

        subject = f"MOM for Meeting {meeting_id}"
        email_body = f"Dear Attendee,\n\nPlease find attached the MOM for meeting {meeting_id}.\n\nBest,\nMeeting Team"

        email_thread = threading.Thread(target=send_email_with_attachments, args=(attendees, subject, email_body, files))
        upload_thread = threading.Thread(target=upload_all_files_to_onedrive, args=(files,))

        email_thread.start()
        upload_thread.start()
        email_thread.join()
        upload_thread.join()

        for filepath in files.values():
            os.remove(filepath)

    except Exception as e:
        print(f"Error in process_and_send_mom: {e}")


@mail_router.post("/send_mom")
def send_mom_endpoint(request: SendMOMRequest, background_tasks: BackgroundTasks):
    """
    API Endpoint to process MOM and send it via email.
    """
    background_tasks.add_task(process_and_send_mom, request.meeting_id, request.attendees)
    return {"message": "MOM processing and email sending started."}
