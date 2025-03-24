

import os
import base64
import requests
import convertapi
import threading
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Initialize FastAPI
app = FastAPI()

# MongoDB connection configuration (update as needed)
client = MongoClient(os.getenv("DB_URL"))
db = client["meeting_db"]
mom_collection = db["meeting_records"]

# Graph API configuration - ensure you have a valid access token.
GRAPH_ACCESS_TOKEN = os.getenv("GRAPH_ACCESS_TOKEN")
GRAPH_SENDMAIL_ENDPOINT = "https://graph.microsoft.com/v1.0/me/microsoft.graph.sendMail"

convertapi.api_credentials = os.getenv("Convert_API")


# Pydantic models
class Attendee(BaseModel):
    name: str
    email: str


class SendMOMRequest(BaseModel):
    meeting_id: str
    attendees: List[Attendee]  # List with name and email


def format_mom_content(mom_data: dict) -> str:
    """
    Formats the mom_data object into a human-readable string.
    """
    lines = []
    lines.append("MINUTES OF MEETING")
    lines.append("=" * 50)
    lines.append("")

    organizer = mom_data.get("organizer", "N/A")
    lines.append(f"Organizer: {organizer}")
    lines.append("")

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
    Generate MOM files in PDF, DOCX, and HTML formats using ConvertAPI.
    The HTML file is created locally, and then converted to PDF and DOCX.
    Returns a dictionary with keys 'pdf', 'docx', and 'html' containing the file paths.
    """
    filenames = {}

    # Create an HTML file from the formatted MOM content.
    # Using <pre> to preserve spacing.
    html_filename = f"mom_{meeting_id}.html"
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(f"<html><body><pre style='font-family: monospace;'>{content}</pre></body></html>")
    filenames["html"] = html_filename

    # Convert HTML to PDF using ConvertAPI
    pdf_filename = f"mom_{meeting_id}.pdf"
    try:
        result_pdf = convertapi.convert('pdf', {'File': html_filename}, from_format='html')
        if not result_pdf or not hasattr(result_pdf, 'file'):
            raise Exception("ConvertAPI did not return a valid PDF conversion result.")
        result_pdf.file.save(pdf_filename)
        filenames["pdf"] = pdf_filename
    except Exception as e:
        print(f"Error converting HTML to PDF: {e}")
        raise

    # Convert HTML to DOCX using ConvertAPI
    docx_filename = f"mom_{meeting_id}.docx"
    try:
        result_docx = convertapi.convert('docx', {'File': html_filename}, from_format='html')
        if not result_docx or not hasattr(result_docx, 'file'):
            raise Exception("ConvertAPI did not return a valid DOCX conversion result.")
        result_docx.file.save(docx_filename)
        filenames["docx"] = docx_filename
    except Exception as e:
        print(f"Error converting HTML to DOCX: {e}")
        raise

    return filenames


def send_email_with_attachments(attendees: List[Attendee], subject: str, body: str, files: dict):
    """
    Sends an email with the provided subject and body along with file attachments using Microsoft Graph API.
    """
    # Prepare recipients list for Graph API
    to_recipients = [{"emailAddress": {"address": att.email}} for att in attendees]

    # Prepare attachments: read files and encode in base64
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

    # Build the email payload
    email_payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body
            },
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
    print("Email sent successfully via Graph API.")


def ensure_onedrive_folder(folder: str) -> str:
    """
    Ensures that the specified folder exists in OneDrive under the root.
    If it doesn't exist, it creates the folder.
    Returns the folder name.
    """
    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder}"
    headers = {
        "Authorization": f"Bearer {GRAPH_ACCESS_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print(f"Folder '{folder}' exists in OneDrive.")
        return folder
    else:
        # Folder does not exist; create it.
        create_url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
        headers["Content-Type"] = "application/json"
        data = {
            "name": folder,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }
        response = requests.post(create_url, headers=headers, json=data)
        if response.status_code in (200, 201):
            print(f"Folder '{folder}' created in OneDrive.")
            return folder
        else:
            raise Exception(f"Failed to create folder {folder} in OneDrive: {response.status_code} - {response.text}")


def upload_file_to_onedrive(filepath: str, folder: str = "MOMFiles"):
    """
    Uploads a file to OneDrive in the specified folder using Microsoft Graph API.
    Ensures that the folder exists first.
    """
    try:
        # Ensure folder exists
        ensure_onedrive_folder(folder)
        filename = os.path.basename(filepath)
        onedrive_path = f"/{folder}/{filename}"
        upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:{onedrive_path}:/content"
        with open(filepath, "rb") as f:
            file_content = f.read()
        headers = {
            "Authorization": f"Bearer {GRAPH_ACCESS_TOKEN}",
            "Content-Type": "application/octet-stream"
        }
        response = requests.put(upload_url, headers=headers, data=file_content)
        if response.status_code in (200, 201):
            print(f"Uploaded {filename} to OneDrive")
        else:
            print(f"Failed to upload {filename} to OneDrive: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error uploading {filename} to OneDrive: {e}")


def upload_all_files_to_onedrive(files: dict):
    """
    Uploads all files in the dictionary to OneDrive.
    """
    for filepath in files.values():
        upload_file_to_onedrive(filepath)


def process_and_send_mom(meeting_id: str, attendees: List[Attendee]):
    """
    Retrieves the MOM data from MongoDB using meeting_id, converts the mom_data object into a formatted string,
    generates MOM files using ConvertAPI, and then concurrently sends an email with attachments and uploads
    the files to OneDrive via Microsoft Graph API.
    """
    try:
        mom_record = mom_collection.find_one({"meeting_id": meeting_id})
        if not mom_record:
            print("MOM record not found in MongoDB for meeting_id:", meeting_id)
            return

        # Convert the mom_data object into a formatted, human-readable string.
        mom_data_obj = mom_record.get("mom_data", {})
        if not mom_data_obj:
            print("MOM content is empty for meeting_id:", meeting_id)
            return

        content = format_mom_content(mom_data_obj)

        # Generate MOM files using ConvertAPI
        files = generate_mom_files(meeting_id, content)

        # Define email subject and body
        subject = f"MOM for Meeting {meeting_id}"
        email_body = f"Dear Attendee,\n\nPlease find attached the MOM for meeting {meeting_id}.\n\nRegards,\nMeeting Team"

        # Create threads for email sending and OneDrive upload concurrently.
        email_thread = threading.Thread(target=send_email_with_attachments,
                                        args=(attendees, subject, email_body, files))
        upload_thread = threading.Thread(target=upload_all_files_to_onedrive, args=(files,))

        email_thread.start()
        upload_thread.start()

        email_thread.join()
        upload_thread.join()

        # Cleanup generated files
        for filepath in files.values():
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Error removing file {filepath}: {e}")

    except Exception as e:
        print(f"Error in process_and_send_mom for meeting_id {meeting_id}: {e}")


@app.post("/send_mom")
def send_mom_endpoint(request: SendMOMRequest, background_tasks: BackgroundTasks):
    """
    Endpoint to send MOM to all attendees via email using Microsoft Graph API and concurrently upload the MOM files to OneDrive.
    Expects a meeting_id and an attendees list (each with name and email).
    """
    background_tasks.add_task(process_and_send_mom, request.meeting_id, request.attendees)
    return {"message": "MOM processing, email sending, and OneDrive upload initiated via Graph API."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)
