import os
import base64
import requests
import convertapi
import threading
import re
import html
import pytz
import datetime
from pymongo import MongoClient
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

class MeetingMailer:
    def __init__(self, db_url: str, db_name: str, collection_name: str, graph_access_token: str):
        self.client = MongoClient(db_url)
        self.db = self.client[db_name]
        self.meeting_records = self.db[collection_name]
        self.graph_access_token = graph_access_token
        # Use your Graph API sendMail endpoint; note the URL format
        self.graph_sendmail_endpoint = "https://graph.microsoft.com/v1.0/me/microsoft.graph.sendMail"
        # Set ConvertAPI credentials (you can also load this from an environment variable)
        convertapi.api_credentials = os.getenv("ConvertAPI")

    def format_mom_content(self, mom_data: dict) -> str:
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

    def generate_mom_files(self, meeting_id: str, content: str) -> dict:
        """
        Generate MOM files in PDF, DOCX, and HTML formats using ConvertAPI.
        The HTML file is created locally, and then converted to PDF and DOCX.
        Returns a dictionary with keys 'pdf', 'docx', and 'html' containing the file paths.
        """
        filenames = {}
        html_filename = f"mom_{meeting_id}.html"
        with open(html_filename, "w", encoding="utf-8") as f:
            f.write(f"<html><body><pre style='font-family: monospace;'>{content}</pre></body></html>")
        filenames["html"] = html_filename

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

    def send_email_with_attachments(self, attendees: list, subject: str, body: str, files: dict):
        """
        Sends an email with the provided subject and body along with file attachments using Microsoft Graph API.
        """
        # Build recipients list
        to_recipients = [{"emailAddress": {"address": att["email"]}} for att in attendees]
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
            "Authorization": f"Bearer {self.graph_access_token}",
            "Content-Type": "application/json"
        }
        response = requests.post(self.graph_sendmail_endpoint, headers=headers, json=email_payload)
        if response.status_code not in (200, 202):
            raise Exception(f"Graph API sendMail failed: {response.status_code} - {response.text}")
        print("Email sent successfully via Graph API.")

    def ensure_onedrive_folder(self, folder: str) -> str:
        """
        Ensures that the specified folder exists in OneDrive under the root.
        If it doesn't exist, creates the folder.
        """
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder}"
        headers = {"Authorization": f"Bearer {self.graph_access_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(f"Folder '{folder}' exists in OneDrive.")
            return folder
        else:
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

    def upload_file_to_onedrive(self, filepath: str, folder: str = "MOMFiles"):
        """
        Uploads a file to OneDrive in the specified folder using Microsoft Graph API.
        """
        try:
            self.ensure_onedrive_folder(folder)
            filename = os.path.basename(filepath)
            onedrive_path = f"/{folder}/{filename}"
            upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:{onedrive_path}:/content"
            with open(filepath, "rb") as f:
                file_content = f.read()
            headers = {
                "Authorization": f"Bearer {self.graph_access_token}",
                "Content-Type": "application/octet-stream"
            }
            response = requests.put(upload_url, headers=headers, data=file_content)
            if response.status_code in (200, 201):
                print(f"Uploaded {filename} to OneDrive")
            else:
                print(f"Failed to upload {filename} to OneDrive: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error uploading {filename} to OneDrive: {e}")

    def upload_all_files_to_onedrive(self, files: dict):
        """
        Uploads all files in the dictionary to OneDrive.
        """
        for filepath in files.values():
            self.upload_file_to_onedrive(filepath)

    def process_and_send_mom(self, meeting_id: str, attendees: list):
        """
        Retrieves the MOM data from MongoDB using meeting_id, converts the mom_data object into a formatted string,
        generates MOM files using ConvertAPI, and then concurrently sends an email with attachments and uploads
        the files to OneDrive via Microsoft Graph API.
        """
        try:
            mom_record = self.meeting_records.find_one({"meeting_id": meeting_id})
            if not mom_record:
                print("MOM record not found in MongoDB for meeting_id:", meeting_id)
                return
            mom_data_obj = mom_record.get("mom_data", {})
            if not mom_data_obj:
                print("MOM content is empty for meeting_id:", meeting_id)
                return
            content = self.format_mom_content(mom_data_obj)
            files = self.generate_mom_files(meeting_id, content)
            subject = f"MOM for Meeting {meeting_id}"
            email_body = f"Dear Attendee,\n\nPlease find attached the MOM for meeting {meeting_id}.\n\nRegards,\nMeeting Team"
            # Create threads for email sending and OneDrive upload concurrently.
            email_thread = threading.Thread(target=self.send_email_with_attachments,
                                            args=(attendees, subject, email_body, files))
            upload_thread = threading.Thread(target=self.upload_all_files_to_onedrive, args=(files,))
            email_thread.start()
            upload_thread.start()
            email_thread.join()
            upload_thread.join()
            for filepath in files.values():
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"Error removing file {filepath}: {e}")
        except Exception as e:
            print(f"Error in process_and_send_mom for meeting_id {meeting_id}: {e}")

