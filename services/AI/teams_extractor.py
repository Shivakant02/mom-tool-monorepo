# import requests
# import json
# from datetime import datetime
# import re
# import html
# import pytz
# from urllib.parse import quote
# from fuzzywuzzy import process  # pip install fuzzywuzzy
# from pymongo import MongoClient
#
#
# # Add MongoDB connection at the top
# client = MongoClient("mongodb+srv://PavanReddy:12345@cluster0.bt0yd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
# db = client["meeting_db"]
# meeting_records = db.meeting_records
#
# def get_latest_meeting_info(access_token):
#     """
#     Retrieves the meeting address, chat ID, and event details for the latest past online meeting.
#
#     Args:
#         access_token (str): Microsoft Graph API access token
#
#     Returns:
#         tuple: (meeting_id, chat_id, event) or raises an exception if not found
#     """
#     # Get current UTC time (no query parameters needed as events are already ordered)
#     now = datetime.utcnow().isoformat() + 'Z'
#     events_url = "https://graph.microsoft.com/v1.0/me/events"
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }
#
#     # Fetch events
#     response = requests.get(events_url, headers=headers)
#     response.raise_for_status()
#     data = response.json()
#     events = data.get("value", [])
#
#     if not events:
#         raise Exception("No past online meetings found.")
#
#     latest_event = events[0]
#     join_url = latest_event.get("onlineMeeting", {}).get("joinUrl")
#     if not join_url:
#         raise Exception("No joinUrl found for the latest meeting.")
#
#     # Extract the meeting address from the joinUrl.
#     # For example, from a joinUrl like:
#     # "https://teams.microsoft.com/l/meetup-join/19%3ameeting_YWIxMTQ0NTktODVjZC00MjUzLWIxYzYtYzMzN2ZmYWY1OWRi@thread.v2/0?context=..."
#     # this regex extracts "19:meeting_YWIxMTQ0NTktODVjZC00MjUzLWIxYzYtYzMzN2ZmYWY1OWRi@thread.v2"
#     match = re.search(r"l/meetup-join/([^/]+)/", join_url)
#     if match:
#         meeting_add = match.group(1)
#     else:
#         raise Exception("Unable to extract meeting address from joinUrl")
#
#     # Use the extracted meeting address as both meeting_id and chat_id
#     meeting_id = meeting_add
#     chat_id = meeting_add
#
#     return meeting_id, chat_id, latest_event
#
#
# def extract_attendees(event):
#     """
#     Extracts the attendees' names and emails from the event data.
#
#     Args:
#         event (dict): The event details as returned by Microsoft Graph
#
#     Returns:
#         list: List of dictionaries containing "name" and "email" for each attendee.
#     """
#     attendees = event.get("attendees", [])
#     result = []
#     for attendee in attendees:
#         email_info = attendee.get("emailAddress", {})
#         name = email_info.get("name")
#         email = email_info.get("address")
#         if name and email:
#             result.append({"name": name, "email": email})
#     return result
#
#
# def extract_teams_chat_messages(access_token, chat_id):
#     """
#     Extracts chat messages from a Microsoft Teams chat.
#
#     Args:
#         access_token (str): Microsoft Graph API access token
#         chat_id (str): The ID of the chat to extract messages from
#
#     Returns:
#         list: List of message dictionaries
#     """
#     url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages"
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }
#     messages = []
#
#     try:
#         while url:
#             response = requests.get(url, headers=headers)
#             response.raise_for_status()
#             data = response.json()
#
#             for msg in data.get("value", []):
#                 if not msg.get("from") or not msg.get("from").get("user"):
#                     continue
#
#                 timestamp = msg.get("createdDateTime")
#                 dt_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
#                 ist_timezone = pytz.timezone('Asia/Kolkata')
#                 ist_time = dt_obj.astimezone(ist_timezone)
#
#                 sender = msg.get("from", {}).get("user", {}).get("displayName", "Unknown User")
#                 content = msg.get("body", {}).get("content", "")
#                 content = re.sub(r'<[^>]*>', ' ', content)
#                 content = html.unescape(content)
#                 content = re.sub(r'\s+', ' ', content).strip()
#
#                 messages.append({
#                     "timestamp": ist_time,
#                     "formatted_time": ist_time.strftime("%Y-%m-%d %H:%M:%S"),
#                     "sender": sender,
#                     "content": content
#                 })
#
#             url = data.get("@odata.nextLink")
#
#         messages.sort(key=lambda x: x["timestamp"])
#         return messages
#
#     except requests.exceptions.HTTPError as http_err:
#         print(f"HTTP error occurred: {http_err}")
#         return []
#     except Exception as err:
#         print(f"Other error occurred: {err}")
#         return []
#
#
# def save_to_text_file(messages, output_file="teams_chat_export.txt"):
#     """
#     Saves the extracted messages to a text file.
#
#     Args:
#         messages (list): List of message dictionaries
#         output_file (str): Path to the output file
#     """
#     try:
#         with open(output_file, "w", encoding="utf-8") as f:
#             f.write("Time | Sender | Message\n")
#             f.write("-" * 100 + "\n")
#             for msg in messages:
#                 f.write(f"{msg['formatted_time']} | {msg['sender']} | {msg['content']}\n\n")
#         print(f"Chat messages successfully exported to {output_file}")
#     except Exception as e:
#         print(f"Error saving to file: {e}")
#
#
# def list_transcripts(access_token, meeting_id):
#     """
#     Lists available transcripts for a given online meeting.
#
#     Args:
#         access_token (str): Microsoft Graph API access token
#         meeting_id (str): The meeting address used as the online meeting ID
#
#     Returns:
#         list: List of transcript metadata
#     """
#     url = f"https://graph.microsoft.com/v1.0/me/onlineMeetings/{meeting_id}/transcripts"
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }
#     response = requests.get(url, headers=headers)
#     response.raise_for_status()
#     data = response.json()
#     return data.get("value", [])
#
#
# def download_transcript_content(access_token, content_url):
#     """
#     Downloads the content of a transcript.
#
#     Args:
#         access_token (str): Microsoft Graph API access token
#         content_url (str): URL to the transcript content
#
#     Returns:
#         bytes: Transcript content in .vtt format
#     """
#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = requests.get(content_url, headers=headers)
#     response.raise_for_status()
#     return response.content
#
#
# def process_transcript(filename, attendees):
#     """
#     Hits the processing API and then applies fuzzy matching to correct action item owner names
#     using the extracted attendees list.
#
#     Args:
#         filename (str): The transcript file name to process (e.g., "MOMTesting.vtt")
#         attendees (list): List of attendee dictionaries with "name" and "email"
#
#     Returns:
#         tuple: (transcript, extracted_info) from the API response
#     """
#     # existing_record = meeting_records.find_one({"meeting_id": meeting_id})
#     #
#     # if existing_record:
#     #     print("Using cached meeting data from MongoDB")
#     #     # Return cached data directly
#     #     mom_data = existing_record.get("mom_data", {})
#     #     corrected_actions = existing_record.get("corrected_action_items", [])
#     #     return corrected_actions, mom_data
#
#     api_url = f"http://localhost:8000/process?filename={filename}"
#     response_AI = requests.get(api_url)
#     response_AI.raise_for_status()
#     data = response_AI.json()
#     # data = {
#     #     "transcript": "Sarah Chen: Alright everyone, let's get started. Thanks for joining today's sprint planning meeting. We have a lot to cover. As you know, we're heading into the final three weeks before the 2.5 release, so we need to prioritize our remaining tasks and address any blockers.\nMarcus Johnson: Before we dive in, I wanted to mention that I've resolved the caching issue we discussed last week. The performance tests are showing a 40% improvement in response time. I've pushed the changes to the development branch if anyone wants to take a look.\nPriya Patel: That's great news, Marcus! I'll review the code later today.\nSarah Chen: Excellent work, Marcus. Priya, can you take a look at it by tomorrow afternoon? It's not very complex, shouldn't take more than an hour.\nPriya Patel: Yes, I can do that, no problem.\nSarah Chen: Great. Just make sure to log any issues you find in Jira so Marcus can address them before the end of the week. Moving on to our main agenda items. The first critical feature we need to complete is the new authentication system. David, can you give us an update on where we stand?\nDavid Kim: Sure. I've implemented the OAuth 2.0 integration, but I'm still having some issues with the token refresh mechanism. I think I'll need another three days to get it fully working. The main challenge is handling token expiration gracefully without disrupting the user experience.\nMarcus Johnson: David, I faced a similar issue on my previous project. I can sit with you after this meeting to share how we solved it.\nDavid Kim: That would be incredibly helpful, thanks Marcus.\nSarah Chen: Great collaboration, team. David, try to wrap up that OAuth token refresh by next Tuesday, okay? We need to leave enough time for testing.\nDavid Kim: Got it. I'll have it done by Tuesday afternoon, assuming there are no major roadblocks.\nSarah Chen: And Marcus, can you sit with David today after the meeting? Maybe around 2 PM?\nMarcus Johnson: Yeah, my calendar's clear after 2. Works for me.\nPriya Patel: While we're on the authentication topic, I've noticed our error messages to users aren't very helpful. Can we improve those as part of this release?\nSarah Chen: Good point, Priya. Do you think you could take that on? Maybe talk to the UX team about the wording?\nPriya Patel: Sure, I can handle that. I'll have something ready by the end of next week.\nSarah Chen: Perfect. Next on our agenda is the new dashboard feature. Marcus, you're leading this effort. How's it coming along?\nMarcus Johnson: The basic structure is in place. I've implemented the widget framework and data fetching layer. Now we need to build the individual visualization components and connect them to the API. I was hoping we could split up the visualization work. There are five main components, and it would speed things up if we divide them among the team.\nDavid Kim: I can take on the metrics chart once I finish the authentication work.\nPriya Patel: I'd be happy to handle the user activity timeline. That aligns well with the work I did on the reporting module last sprint.\nSarah Chen: I can work on the status overview widget. That leaves the resource allocation chart and the alerts panel.\nMarcus Johnson: I'll take those two. Can everyone get their components done by next Friday?\nDavid Kim: Should be doable.\nPriya Patel: Works for me.\nSarah Chen: I'll add these assignments to our sprint board after the meeting.\nDavid Kim: I have a concern about the upcoming API changes. The backend team mentioned they're refactoring the endpoints we're using for the dashboard. Has anyone spoken with them about this?\nSarah Chen: Good point, David. I wasn't aware of that. We need to coordinate with them.\nMarcus Johnson: I'll talk to Raj from the backend team tomorrow. Can find out what their timeline looks like.\nDavid Kim: I'd like to join that conversation since my work depends heavily on their APIs.\nMarcus Johnson: Sure, I'll set something up for tomorrow morning and send you a calendar invite.\nSarah Chen: Let's move on to discuss our testing strategy for this release. We need to make sure we have comprehensive test coverage, especially for the new features.\nPriya Patel: I've been working on expanding our unit test suite. Currently, we're at about 78% coverage, but I'd like to get that above 85% before the release. I've also set up the integration tests for the authentication flow, but we'll need similar tests for the dashboard.\nMarcus Johnson: I'll write the integration tests for the dashboard once all the components are in place. Should we also consider adding some end-to-end tests?\nDavid Kim: End-to-end tests would be valuable, especially for the critical user journeys. I can set up the framework and write a few examples, then we can all contribute.\nSarah Chen: David, how long would it take you to set up that framework?\nDavid Kim: I can have it ready by next Thursday if I start after finishing the authentication work.\nSarah Chen: That works. Priya, can you hit that 85% coverage target by the end of the month?\nPriya Patel: Yes, that shouldn't be a problem. I'll focus on the critical paths first.\nSarah Chen: And Marcus, aim to have those dashboard integration tests done by the end of the month, okay?\nMarcus Johnson: Got it. I'll start once all the dashboard components are ready.\nSarah Chen: Finally, let's talk about documentation. We need to update the developer docs for the new features and create user guides for the dashboard.\nPriya Patel: I can update the API documentation to reflect any changes. Should we involve the technical writing team for the user guides?\nSarah Chen: Yes, definitely. I'll talk to Julia from the documentation team this week about collaborating on the user guides.\nDavid Kim: I'll handle the developer documentation for the authentication system once it's complete.\nMarcus Johnson: And I'll write up the technical details for the dashboard framework for the documentation team.\nSarah Chen: Great, let's try to have all docs wrapped up by the first week of April.\nPriya Patel: That's fine for the API docs. I can have them ready by April 2nd if that works?\nSarah Chen: That's perfect, Priya. David and Marcus, same timeframe work for you?\nDavid Kim: I can have the auth docs done by the end of the month.\nMarcus Johnson: Same here for the dashboard documentation.\nSarah Chen: Great job, team. I think we have a solid plan for the final push to the 2.5 release. Any other concerns or issues we should discuss?\nDavid Kim: I'll be out next Tuesday morning for a doctor's appointment, just so everyone knows.\nSarah Chen: Thanks for letting us know, David.\nMarcus Johnson: I've scheduled a demo of the dashboard framework for next Wednesday at 2 PM. Would be great if you all could attend and give feedback.\nPriya Patel: I've added it to my calendar. Looking forward to it.\nDavid Kim: I'll be there too. Will you send the meeting link?\nMarcus Johnson: Yeah, I'll send out a calendar invite right after this.\nSarah Chen: Perfect. Let's meet again same time next week to check on our progress. Make sure to keep your Jira tickets updated as you go. Any final questions? Alright then. Thanks everyone for your time. Let's have a great sprint!\nMarcus Johnson: Thanks, Sarah. Bye everyone!\nPriya Patel: Thanks, bye!\nDavid Kim: Thanks for running the meeting, Sarah. Talk to you all later.",
#     #     "extracted_info": "{\n  \"organizer\": \"Sarah Chen\",\n  \"discussion_topics\": [\n    \"Sprint planning for 2.5 release\",\n    \"Authentication system update\",\n    \"New dashboard feature progress\",\n    \"Testing strategy for the release\",\n    \"Documentation updates\"\n  ],\n  \"key_points\": [\n    \"Marcus resolved the caching issue with a 40% improvement in response time.\",\n    \"David is working on the OAuth 2.0 integration but needs three more days for the token refresh mechanism.\",\n    \"Team members agreed to split the work on the new dashboard feature.\",\n    \"Priya aims to increase unit test coverage to above 85% before the release.\",\n    \"Documentation updates are needed for the new features, with specific assignments.\"\n  ],\n  \"faqs\": [\n    \"What is the status of the OAuth token refresh mechanism?\",\n    \"How are we dividing the work for the dashboard feature?\",\n    \"What is our testing strategy for the new features?\",\n    \"When are the documentation updates due?\"\n  ],\n  \"action_items\": [\n    {\n      \"item\": \"Review caching code changes\",\n      \"deadline\": \"Tomorrow afternoon\",\n      \"owner\": \"Priya Patel\"\n    },\n    {\n      \"item\": \"Complete OAuth token refresh mechanism\",\n      \"deadline\": \"Next Tuesday afternoon\",\n      \"owner\": \"pavbn\"\n    },\n    {\n      \"item\": \"Pair with David to resolve OAuth issues\",\n      \"deadline\": \"Today at 2 PM\",\n      \"owner\": \"Lokesh\"\n    },\n    {\n      \"item\": \"Improve user error messages\",\n      \"deadline\": \"End of next week\",\n      \"owner\": \"shivakant\"\n    },\n    {\n      \"item\": \"Complete metrics chart for dashboard\",\n      \"deadline\": \"Next Friday\",\n      \"owner\": \"David Kim\"\n    },\n    {\n      \"item\": \"Complete user activity timeline for dashboard\",\n      \"deadline\": \"Next Friday\",\n      \"owner\": \"Priya Patel\"\n    },\n    {\n      \"item\": \"Complete status overview widget for dashboard\",\n      \"deadline\": \"Next Friday\",\n      \"owner\": \"Sarah Chen\"\n    },\n    {\n      \"item\": \"Complete resource allocation chart and alerts panel for dashboard\",\n      \"deadline\": \"Next Friday\",\n      \"owner\": \"Marcus Johnson\"\n    },\n    {\n      \"item\": \"Set up end-to-end testing framework\",\n      \"deadline\": \"Next Thursday\",\n      \"owner\": \"David Kim\"\n    },\n    {\n      \"item\": \"Reach 85% test coverage\",\n      \"deadline\": \"End of the month\",\n      \"owner\": \"Priya Patel\"\n    },\n    {\n      \"item\": \"Complete dashboard integration tests\",\n      \"deadline\": \"End of the month\",\n      \"owner\": \"Marcus Johnson\"\n    },\n    {\n      \"item\": \"Update API documentation\",\n      \"deadline\": \"April 2nd\",\n      \"owner\": \"Priya Patel\"\n    },\n    {\n      \"item\": \"Handle developer documentation for authentication system\",\n      \"deadline\": \"End of the month\",\n      \"owner\": \"David Kim\"\n    },\n    {\n      \"item\": \"Write technical details for dashboard framework documentation\",\n      \"deadline\": \"End of the month\",\n      \"owner\": \"Marcus Johnson\"\n    }\n  ]\n}"
#     # }
#     transcript = data.get("transcript")
#     extracted_info_str = data.get("extracted_info")
#     # Parse the extracted_info JSON string
#     extracted_info = json.loads(extracted_info_str)
#     action_items = extracted_info.get("action_items", [])
#     original_names = [item.get("owner") for item in action_items]
#     # Build a list of attendee names for fuzzy matching
#     attendee_names = [att["name"] for att in attendees]
#
#     # Correct action item owner names using fuzzy matching (threshold set to 80)
#     url = "http://localhost:8000/match"
#     payload = {
#         "names_list": original_names,
#         "attendees_list": attendee_names
#     }
#
#     response_Match = requests.post(url, json=payload)
#     result_json = response_Match.json()
#     result_str = result_json.get("result")
#
#     # Extract the JSON content from the backticks
#     match = re.search(r"```json\n(.*?)\n```", result_str, re.DOTALL)
#     if match:
#         json_content = match.group(1)
#         matches_list = json.loads(json_content)
#     else:
#         matches_list = []
#
#     for match_item in matches_list:
#         original_name = match_item.get("Original_Name")
#         matched_attendee = match_item.get("Matched_Attendee")
#         # Only update if a reasonable match is found
#         if matched_attendee != "Unmatched":
#             for item in action_items:
#                 if item.get("owner") == original_name:
#                     # Find the attendee details from the attendees list
#                     attendee_detail = next((att for att in attendees if att["name"] == matched_attendee), None)
#                     if attendee_detail:
#                         print(
#                             f"Correcting owner: {original_name} -> {matched_attendee} with email {attendee_detail.get('email')}")
#                         item["owner"] = matched_attendee
#                         item["email"] = attendee_detail.get("email")
#                     else:
#                         # If no matching attendee detail is found, update only the owner name.
#                         print(f"Correcting owner: {original_name} -> {matched_attendee} (no email found)")
#                         item["owner"] = matched_attendee
#
#     return action_items,extracted_info
#
#
# def main():
#     # Replace with your actual access token
#     access_token = "eyJ0eXAiOiJKV1QiLCJub25jZSI6Ijk5MHhHcWtRTllhQmhOUDNSajNDSmNHUWdGZ2xHTV9QNmpzRzcxYVhMYkUiLCJhbGciOiJSUzI1NiIsIng1dCI6IkpETmFfNGk0cjdGZ2lnTDNzSElsSTN4Vi1JVSIsImtpZCI6IkpETmFfNGk0cjdGZ2lnTDNzSElsSTN4Vi1JVSJ9.eyJhdWQiOiIwMDAwMDAwMy0wMDAwLTAwMDAtYzAwMC0wMDAwMDAwMDAwMDAiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC81ODdjMDJjZS1iMjk0LTQ0YmItOGZkNi0wZjU2OTU1MDhkMjgvIiwiaWF0IjoxNzQyNjcyMTAxLCJuYmYiOjE3NDI2NzIxMDEsImV4cCI6MTc0Mjc1ODgwMSwiYWNjdCI6MCwiYWNyIjoiMSIsImFpbyI6IkFVUUF1LzhaQUFBQVVNUmt3eU5yVHpYeU80OEVHaEtZdWUvTEs4YWNyYmVWWFlmMXRzNXVlOFlKdER0VU4vMWNnbU03N2JQNzU0MlVFQ01KVE9tdFZoODRrcTFObHpCeTRBPT0iLCJhbXIiOlsicHdkIl0sImFwcF9kaXNwbGF5bmFtZSI6IkdyYXBoIEV4cGxvcmVyIiwiYXBwaWQiOiJkZThiYzhiNS1kOWY5LTQ4YjEtYThhZC1iNzQ4ZGE3MjUwNjQiLCJhcHBpZGFjciI6IjAiLCJmYW1pbHlfbmFtZSI6IlBhdmFuIiwiZ2l2ZW5fbmFtZSI6IksiLCJpZHR5cCI6InVzZXIiLCJpcGFkZHIiOiIxMDQuMjguMjI1LjE0IiwibmFtZSI6IksgUGF2YW4iLCJvaWQiOiJjYjUyYzQwMy0yZGJjLTQ0YzMtOWMyZC01NzdiN2M0ZTI1YzUiLCJwbGF0ZiI6IjUiLCJwdWlkIjoiMTAwMzIwMDQzMjMzMjZDRCIsInJoIjoiMS5BWEFBemdKOFdKU3l1MFNQMWc5V2xWQ05LQU1BQUFBQUFBQUF3QUFBQUFBQUFBREVBTjV3QUEuIiwic2NwIjoiQ2FsZW5kYXJzLlJlYWQgQ2FsZW5kYXJzLlJlYWRCYXNpYyBDYWxlbmRhcnMuUmVhZFdyaXRlIENoYXQuUmVhZCBDaGF0LlJlYWRXcml0ZSBvcGVuaWQgcHJvZmlsZSBUZWFtc0FjdGl2aXR5LlJlYWQgVXNlci5SZWFkIFVzZXIuUmVhZC5BbGwgZW1haWwiLCJzaWQiOiIwMDMxMDJmOS00ZTg2LTljMDYtNmE4ZC05NmNmOGYyNzgxNjYiLCJzaWduaW5fc3RhdGUiOlsia21zaSJdLCJzdWIiOiJDRWJLNk53Mk9ZQ0tmTVdqdWw2YXdLSTZTRnVNS0p3bkZicWh6V2NOTWhJIiwidGVuYW50X3JlZ2lvbl9zY29wZSI6IkFTIiwidGlkIjoiNTg3YzAyY2UtYjI5NC00NGJiLThmZDYtMGY1Njk1NTA4ZDI4IiwidW5pcXVlX25hbWUiOiJrLnBhdmFuQGx1bWlxLmFpIiwidXBuIjoiay5wYXZhbkBsdW1pcS5haSIsInV0aSI6ImtrbzRrZ2RuSlV1SmJ4dW9rbnNRQUEiLCJ2ZXIiOiIxLjAiLCJ3aWRzIjpbImNmMWMzOGU1LTM2MjEtNDAwNC1hN2NiLTg3OTYyNGRjZWQ3YyIsImYyZWY5OTJjLTNhZmItNDZiOS1iN2NmLWExMjZlZTc0YzQ1MSIsImI3OWZiZjRkLTNlZjktNDY4OS04MTQzLTc2YjE5NGU4NTUwOSJdLCJ4bXNfY2MiOlsiQ1AxIl0sInhtc19mdGQiOiI0c0dmYm44eTBtSnd0WnVjOHdFMzZnUTF4Z2Z1UWxNZ1pnRnQ5RFZicDdVIiwieG1zX2lkcmVsIjoiMSAzMiIsInhtc19zc20iOiIxIiwieG1zX3N0Ijp7InN1YiI6Ijd5R203Q21GSTJMRXJvbVlicmVnVURUMU5tQjRBeTY4NjJlOGxoLUlUOEEifSwieG1zX3RjZHQiOjE2MjQxMDQ4NzV9.Oynv6HupVNbPwuEk4DGK8AOTEKag39j5HZyYfg9C1zJ_zsmfvICVWXLAOvQnktEzn3UQj0I82aLbx0vS6JTS2yg9jttfuqB0RJbKk9I3BXDOabWvbri0zraNtaSRUkjBFXGMozyDzbbsthHegSA3fyVdwco4Z6IXoyXdkJL4qYjJH-xQYHcpGQxEszB6k_Qq3hiW88k1gdjWyVKgMVGWVclYrydRxW4XAAt-Sm_pEOPXhib3LNDgItEPqZAeDysRcYfxlqmuxxvmW8PwFXh4n5c0C_ipjioYUrWjVHQ7U-p7XY9elMl5ps52E9HqzRABiG1yzVLtY6e1DtU5tOEE8A"
#     try:
#         # Get info for the latest meeting and extract meeting address & chat id
#         meeting_id, chat_id, event = get_latest_meeting_info(access_token)
#         meeting_subject = event.get('subject', 'Unnamed Meeting')
#         print(f"Processing meeting: {meeting_subject}")
#
#         # Check MongoDB for existing record
#         existing_record = meeting_records.find_one({"meeting_id": meeting_id})
#
#         if existing_record:
#             print("Found cached meeting data in MongoDB")
#             # Return cached data
#             print("\nCached MOM Data:")
#             print(json.dumps(existing_record["mom_data"], indent=2))
#             print("\nCached Corrected Action Items:")
#             print(json.dumps(existing_record["corrected_action_items"], indent=2))
#             return
#
#         # Extract attendees list from the event
#         attendees = extract_attendees(event)
#
#         # Extract and save chat messages
#         messages = extract_teams_chat_messages(access_token, chat_id)
#         if messages:
#             start_time = event["start"]["dateTime"]
#             start_time_str = datetime.fromisoformat(start_time.replace('Z', '+00:00')).strftime("%Y%m%d_%H%M%S")
#             chat_filename = f"chat_{start_time_str}.txt"
#             save_to_text_file(messages, chat_filename)
#         else:
#             print("No chat messages found.")
#
#         # Extract and save transcripts (if available)
#         transcripts = list_transcripts(access_token, meeting_id)
#         if transcripts:
#             for transcript_meta in transcripts:
#                 transcript_id = transcript_meta["id"]
#                 content_url = transcript_meta["contentUrl"]
#                 content = download_transcript_content(access_token, content_url)
#                 transcript_filename = f"transcript_{transcript_id}_{start_time_str}.vtt"
#                 with open(transcript_filename, "wb") as f:
#                     f.write(content)
#                 print(f"Transcript saved to {transcript_filename}")
#         else:
#             print("No transcripts found for this meeting.")
#
#         Finalitems,MOM = process_transcript("MOMTesting.vtt", attendees)
#         mom_data=MOM
#         meeting_record = {
#             "meeting_id": meeting_id,
#             "meeting_subject": meeting_subject,
#             "meeting_time": datetime.fromisoformat(event["start"]["dateTime"].replace('Z', '+00:00')),
#             "attendees": attendees,
#             "mom_data": mom_data,
#             "corrected_action_items": Finalitems,
#             "processed_at": datetime.now()
#         }
#
#         result = meeting_records.insert_one(meeting_record)
#         print(f"\nSuccessfully stored meeting data in MongoDB (ID: {result.inserted_id})")
#
#         print("\nFreshly Generated MOM Data:")
#         print(json.dumps(mom_data, indent=2))
#         print("\nFreshly Generated Action Items:")
#         print(json.dumps(Finalitems, indent=2))
#
#     except Exception as e:
#         print(f"An error occurred: {e}")
#
#
#
# if __name__ == "__main__":
#     main()


#Main code is below


# import os
#
# import requests
# import json
# import re
# import html
# import pytz
# from datetime import datetime
# from fuzzywuzzy import process  # pip install fuzzywuzzy
# from urllib.parse import quote
# from pymongo import MongoClient
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from dotenv import load_dotenv
# import uvicorn
#
# load_dotenv()
#
# app = FastAPI()
#
# # MongoDB connection
# client = MongoClient(os.getenv("DB_URL"))
# db = client["meeting_db"]
# meeting_records = db.meeting_records
#
# def get_latest_meeting_info(access_token):
#     """
#     Retrieves the meeting address, chat ID, and event details for the latest past online meeting.
#     """
#     now = datetime.utcnow().isoformat() + 'Z'
#     events_url = "https://graph.microsoft.com/v1.0/me/events"
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }
#     response = requests.get(events_url, headers=headers)
#     response.raise_for_status()
#     data = response.json()
#     events = data.get("value", [])
#     if not events:
#         raise Exception("No past online meetings found.")
#     latest_event = events[0]
#     join_url = latest_event.get("onlineMeeting", {}).get("joinUrl")
#     if not join_url:
#         raise Exception("No joinUrl found for the latest meeting.")
#     # Extract the meeting address from the joinUrl
#     match = re.search(r"l/meetup-join/([^/]+)/", join_url)
#     if match:
#         meeting_add = match.group(1)
#     else:
#         raise Exception("Unable to extract meeting address from joinUrl")
#     meeting_id = meeting_add
#     chat_id = meeting_add
#     return meeting_id, chat_id, latest_event
#
# def extract_attendees(event):
#     """
#     Extracts the attendees' names and emails from the event data.
#     """
#     attendees = event.get("attendees", [])
#     result = []
#     for attendee in attendees:
#         email_info = attendee.get("emailAddress", {})
#         name = email_info.get("name")
#         email = email_info.get("address")
#         if name and email:
#             result.append({"name": name, "email": email})
#     return result
#
# def extract_teams_chat_messages(access_token, chat_id):
#     """
#     Extracts chat messages from a Microsoft Teams chat.
#     """
#     url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages"
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }
#     messages = []
#     try:
#         while url:
#             response = requests.get(url, headers=headers)
#             response.raise_for_status()
#             data = response.json()
#
#             for msg in data.get("value", []):
#                 if not msg.get("from") or not msg.get("from").get("user"):
#                     continue
#                 timestamp = msg.get("createdDateTime")
#                 dt_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
#                 ist_timezone = pytz.timezone('Asia/Kolkata')
#                 ist_time = dt_obj.astimezone(ist_timezone)
#
#                 sender = msg.get("from", {}).get("user", {}).get("displayName", "Unknown User")
#                 content = msg.get("body", {}).get("content", "")
#                 content = re.sub(r'<[^>]*>', ' ', content)
#                 content = html.unescape(content)
#                 content = re.sub(r'\s+', ' ', content).strip()
#
#                 messages.append({
#                     "timestamp": ist_time,
#                     "formatted_time": ist_time.strftime("%Y-%m-%d %H:%M:%S"),
#                     "sender": sender,
#                     "content": content
#                 })
#
#             url = data.get("@odata.nextLink")
#
#         messages.sort(key=lambda x: x["timestamp"])
#         return messages
#
#     except Exception as err:
#         print(f"Error extracting chat messages: {err}")
#         return []
#
# def save_to_text_file(messages, output_file="teams_chat_export.txt"):
#     """
#     Saves the extracted messages to a text file.
#     """
#     try:
#         with open(output_file, "w", encoding="utf-8") as f:
#             f.write("Time | Sender | Message\n")
#             f.write("-" * 100 + "\n")
#             for msg in messages:
#                 f.write(f"{msg['formatted_time']} | {msg['sender']} | {msg['content']}\n\n")
#         print(f"Chat messages successfully exported to {output_file}")
#     except Exception as e:
#         print(f"Error saving to file: {e}")
#
# def list_transcripts(access_token, meeting_id):
#     """
#     Lists available transcripts for a given online meeting.
#     """
#     url = f"https://graph.microsoft.com/v1.0/me/onlineMeetings/{meeting_id}/transcripts"
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }
#     response = requests.get(url, headers=headers)
#     response.raise_for_status()
#     data = response.json()
#     return data.get("value", [])
#
# def download_transcript_content(access_token, content_url):
#     """
#     Downloads the content of a transcript.
#     """
#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = requests.get(content_url, headers=headers)
#     response.raise_for_status()
#     return response.content
#
# def process_transcript(filename, attendees):
#     """
#     Hits the processing API and then applies fuzzy matching to correct action item owner names
#     using the extracted attendees list.
#     """
#     # api_url = f"http://localhost:8001/process?filename={filename}"
#     # response_AI = requests.get(api_url)
#     # response_AI.raise_for_status()
#     # data = response_AI.json()
#     data = {
#             "transcript": "Sarah Chen: Alright everyone, let's get started. Thanks for joining today's sprint planning meeting. We have a lot to cover. As you know, we're heading into the final three weeks before the 2.5 release, so we need to prioritize our remaining tasks and address any blockers.\nMarcus Johnson: Before we dive in, I wanted to mention that I've resolved the caching issue we discussed last week. The performance tests are showing a 40% improvement in response time. I've pushed the changes to the development branch if anyone wants to take a look.\nPriya Patel: That's great news, Marcus! I'll review the code later today.\nSarah Chen: Excellent work, Marcus. Priya, can you take a look at it by tomorrow afternoon? It's not very complex, shouldn't take more than an hour.\nPriya Patel: Yes, I can do that, no problem.\nSarah Chen: Great. Just make sure to log any issues you find in Jira so Marcus can address them before the end of the week. Moving on to our main agenda items. The first critical feature we need to complete is the new authentication system. David, can you give us an update on where we stand?\nDavid Kim: Sure. I've implemented the OAuth 2.0 integration, but I'm still having some issues with the token refresh mechanism. I think I'll need another three days to get it fully working. The main challenge is handling token expiration gracefully without disrupting the user experience.\nMarcus Johnson: David, I faced a similar issue on my previous project. I can sit with you after this meeting to share how we solved it.\nDavid Kim: That would be incredibly helpful, thanks Marcus.\nSarah Chen: Great collaboration, team. David, try to wrap up that OAuth token refresh by next Tuesday, okay? We need to leave enough time for testing.\nDavid Kim: Got it. I'll have it done by Tuesday afternoon, assuming there are no major roadblocks.\nSarah Chen: And Marcus, can you sit with David today after the meeting? Maybe around 2 PM?\nMarcus Johnson: Yeah, my calendar's clear after 2. Works for me.\nPriya Patel: While we're on the authentication topic, I've noticed our error messages to users aren't very helpful. Can we improve those as part of this release?\nSarah Chen: Good point, Priya. Do you think you could take that on? Maybe talk to the UX team about the wording?\nPriya Patel: Sure, I can handle that. I'll have something ready by the end of next week.\nSarah Chen: Perfect. Next on our agenda is the new dashboard feature. Marcus, you're leading this effort. How's it coming along?\nMarcus Johnson: The basic structure is in place. I've implemented the widget framework and data fetching layer. Now we need to build the individual visualization components and connect them to the API. I was hoping we could split up the visualization work. There are five main components, and it would speed things up if we divide them among the team.\nDavid Kim: I can take on the metrics chart once I finish the authentication work.\nPriya Patel: I'd be happy to handle the user activity timeline. That aligns well with the work I did on the reporting module last sprint.\nSarah Chen: I can work on the status overview widget. That leaves the resource allocation chart and the alerts panel.\nMarcus Johnson: I'll take those two. Can everyone get their components done by next Friday?\nDavid Kim: Should be doable.\nPriya Patel: Works for me.\nSarah Chen: I'll add these assignments to our sprint board after the meeting.\nDavid Kim: I have a concern about the upcoming API changes. The backend team mentioned they're refactoring the endpoints we're using for the dashboard. Has anyone spoken with them about this?\nSarah Chen: Good point, David. I wasn't aware of that. We need to coordinate with them.\nMarcus Johnson: I'll talk to Raj from the backend team tomorrow. Can find out what their timeline looks like.\nDavid Kim: I'd like to join that conversation since my work depends heavily on their APIs.\nMarcus Johnson: Sure, I'll set something up for tomorrow morning and send you a calendar invite.\nSarah Chen: Let's move on to discuss our testing strategy for this release. We need to make sure we have comprehensive test coverage, especially for the new features.\nPriya Patel: I've been working on expanding our unit test suite. Currently, we're at about 78% coverage, but I'd like to get that above 85% before the release. I've also set up the integration tests for the authentication flow, but we'll need similar tests for the dashboard.\nMarcus Johnson: I'll write the integration tests for the dashboard once all the components are in place. Should we also consider adding some end-to-end tests?\nDavid Kim: End-to-end tests would be valuable, especially for the critical user journeys. I can set up the framework and write a few examples, then we can all contribute.\nSarah Chen: David, how long would it take you to set up that framework?\nDavid Kim: I can have it ready by next Thursday if I start after finishing the authentication work.\nSarah Chen: That works. Priya, can you hit that 85% coverage target by the end of the month?\nPriya Patel: Yes, that shouldn't be a problem. I'll focus on the critical paths first.\nSarah Chen: And Marcus, aim to have those dashboard integration tests done by the end of the month, okay?\nMarcus Johnson: Got it. I'll start once all the dashboard components are ready.\nSarah Chen: Finally, let's talk about documentation. We need to update the developer docs for the new features and create user guides for the dashboard.\nPriya Patel: I can update the API documentation to reflect any changes. Should we involve the technical writing team for the user guides?\nSarah Chen: Yes, definitely. I'll talk to Julia from the documentation team this week about collaborating on the user guides.\nDavid Kim: I'll handle the developer documentation for the authentication system once it's complete.\nMarcus Johnson: And I'll write up the technical details for the dashboard framework for the documentation team.\nSarah Chen: Great, let's try to have all docs wrapped up by the first week of April.\nPriya Patel: That's fine for the API docs. I can have them ready by April 2nd if that works?\nSarah Chen: That's perfect, Priya. David and Marcus, same timeframe work for you?\nDavid Kim: I can have the auth docs done by the end of the month.\nMarcus Johnson: Same here for the dashboard documentation.\nSarah Chen: Great job, team. I think we have a solid plan for the final push to the 2.5 release. Any other concerns or issues we should discuss?\nDavid Kim: I'll be out next Tuesday morning for a doctor's appointment, just so everyone knows.\nSarah Chen: Thanks for letting us know, David.\nMarcus Johnson: I've scheduled a demo of the dashboard framework for next Wednesday at 2 PM. Would be great if you all could attend and give feedback.\nPriya Patel: I've added it to my calendar. Looking forward to it.\nDavid Kim: I'll be there too. Will you send the meeting link?\nMarcus Johnson: Yeah, I'll send out a calendar invite right after this.\nSarah Chen: Perfect. Let's meet again same time next week to check on our progress. Make sure to keep your Jira tickets updated as you go. Any final questions? Alright then. Thanks everyone for your time. Let's have a great sprint!\nMarcus Johnson: Thanks, Sarah. Bye everyone!\nPriya Patel: Thanks, bye!\nDavid Kim: Thanks for running the meeting, Sarah. Talk to you all later.",
#             "extracted_info": "{\n  \"organizer\": \"Sarah Chen\",\n  \"discussion_topics\": [\n    \"Sprint planning for 2.5 release\",\n    \"Authentication system update\",\n    \"New dashboard feature progress\",\n    \"Testing strategy for the release\",\n    \"Documentation updates\"\n  ],\n  \"key_points\": [\n    \"Marcus resolved the caching issue with a 40% improvement in response time.\",\n    \"David is working on the OAuth 2.0 integration but needs three more days for the token refresh mechanism.\",\n    \"Team members agreed to split the work on the new dashboard feature.\",\n    \"Priya aims to increase unit test coverage to above 85% before the release.\",\n    \"Documentation updates are needed for the new features, with specific assignments.\"\n  ],\n  \"faqs\": [\n    \"What is the status of the OAuth token refresh mechanism?\",\n    \"How are we dividing the work for the dashboard feature?\",\n    \"What is our testing strategy for the new features?\",\n    \"When are the documentation updates due?\"\n  ],\n  \"action_items\": [\n    {\n      \"item\": \"Review caching code changes\",\n      \"deadline\": \"Tomorrow afternoon\",\n      \"owner\": \"Priya Patel\"\n    },\n    {\n      \"item\": \"Complete OAuth token refresh mechanism\",\n      \"deadline\": \"Next Tuesday afternoon\",\n      \"owner\": \"pavbn\"\n    },\n    {\n      \"item\": \"Pair with David to resolve OAuth issues\",\n      \"deadline\": \"Today at 2 PM\",\n      \"owner\": \"Lokesh\"\n    },\n    {\n      \"item\": \"Improve user error messages\",\n      \"deadline\": \"End of next week\",\n      \"owner\": \"shivakant\"\n    },\n    {\n      \"item\": \"Complete metrics chart for dashboard\",\n      \"deadline\": \"Next Friday\",\n      \"owner\": \"David Kim\"\n    },\n    {\n      \"item\": \"Complete user activity timeline for dashboard\",\n      \"deadline\": \"Next Friday\",\n      \"owner\": \"Priya Patel\"\n    },\n    {\n      \"item\": \"Complete status overview widget for dashboard\",\n      \"deadline\": \"Next Friday\",\n      \"owner\": \"Sarah Chen\"\n    },\n    {\n      \"item\": \"Complete resource allocation chart and alerts panel for dashboard\",\n      \"deadline\": \"Next Friday\",\n      \"owner\": \"Marcus Johnson\"\n    },\n    {\n      \"item\": \"Set up end-to-end testing framework\",\n      \"deadline\": \"Next Thursday\",\n      \"owner\": \"David Kim\"\n    },\n    {\n      \"item\": \"Reach 85% test coverage\",\n      \"deadline\": \"End of the month\",\n      \"owner\": \"Priya Patel\"\n    },\n    {\n      \"item\": \"Complete dashboard integration tests\",\n      \"deadline\": \"End of the month\",\n      \"owner\": \"Marcus Johnson\"\n    },\n    {\n      \"item\": \"Update API documentation\",\n      \"deadline\": \"April 2nd\",\n      \"owner\": \"Priya Patel\"\n    },\n    {\n      \"item\": \"Handle developer documentation for authentication system\",\n      \"deadline\": \"End of the month\",\n      \"owner\": \"David Kim\"\n    },\n    {\n      \"item\": \"Write technical details for dashboard framework documentation\",\n      \"deadline\": \"End of the month\",\n      \"owner\": \"Marcus Johnson\"\n    }\n  ]\n}"
#         }
#     transcript = data.get("transcript")
#     extracted_info_str = data.get("extracted_info")
#     try:
#         extracted_info = json.loads(extracted_info_str)
#     except Exception:
#         extracted_info = extracted_info_str
#     action_items = extracted_info.get("action_items", [])
#     original_names = [item.get("owner") for item in action_items]
#     attendee_names = [att["name"] for att in attendees]
#
#     # Hit the matching API to correct names
#     url = "http://localhost:8000/match"
#     payload = {
#         "names_list": original_names,
#         "attendees_list": attendee_names
#     }
#     response_Match = requests.post(url, json=payload)
#     result_json = response_Match.json()
#     result_str = result_json.get("result")
#
#     # Extract JSON content from backticks if present
#     match_res = re.search(r"```json\n(.*?)\n```", result_str, re.DOTALL)
#     if match_res:
#         json_content = match_res.group(1)
#         try:
#             matches_list = json.loads(json_content)
#         except Exception as e:
#             print("Error parsing JSON from match result:", e)
#             matches_list = []
#     else:
#         matches_list = []
#
#     # Update the action items with corrected owner names
#     for match_item in matches_list:
#         original_name = match_item.get("Original_Name")
#         matched_attendee = match_item.get("Matched_Attendee")
#         if matched_attendee != "Unmatched":
#             for item in action_items:
#                 if item.get("owner") == original_name:
#                     attendee_detail = next((att for att in attendees if att["name"] == matched_attendee), None)
#                     if attendee_detail:
#                         print(f"Correcting owner: {original_name} -> {matched_attendee} with email {attendee_detail.get('email')}")
#                         item["owner"] = matched_attendee
#                         item["email"] = attendee_detail.get("email")
#                     else:
#                         print(f"Correcting owner: {original_name} -> {matched_attendee} (no email found)")
#                         item["owner"] = matched_attendee
#     return action_items, extracted_info
#
# @app.get("/process_meeting")
# def process_meeting():
#     """
#     Processes the latest meeting by retrieving meeting and chat details,
#     processing the transcript, and returning the MOM data and corrected action items.
#     """
#     # Replace with your actual access token or pass it as a parameter
#     access_token = os.getenv("GRAPH_ACCESS_TOKEN")
#     try:
#         meeting_id, chat_id, event = get_latest_meeting_info(access_token)
#         meeting_subject = event.get('subject', 'Unnamed Meeting')
#         print(f"Processing meeting: {meeting_subject} {meeting_id}")
#
#         # Check for existing meeting record in MongoDB
#         existing_record = meeting_records.find_one({"meeting_id": meeting_id})
#         if existing_record:
#             print("Found cached meeting data in MongoDB")
#             return {
#                 "mom_data": existing_record["mom_data"]
#             }
#
#         attendees = extract_attendees(event)
#
#         # Extract Teams chat messages and save them to file
#         messages = extract_teams_chat_messages(access_token, chat_id)
#         if messages:
#             start_time = event["start"]["dateTime"]
#             start_time_str = datetime.fromisoformat(start_time.replace('Z', '+00:00')).strftime("%Y%m%d_%H%M%S")
#             chat_filename = f"chat_{start_time_str}.txt"
#             save_to_text_file(messages, chat_filename)
#         else:
#             print("No chat messages found.")
#
#         # Process transcripts if available
#         # transcripts = list_transcripts(access_token, meeting_id)
#         # if transcripts:
#         #     for transcript_meta in transcripts:
#         #         transcript_id = transcript_meta["id"]
#         #         content_url = transcript_meta["contentUrl"]
#         #         content = download_transcript_content(access_token, content_url)
#         #         transcript_filename = f"transcript_{transcript_id}_{start_time_str}.vtt"
#         #         with open(transcript_filename, "wb") as f:
#         #             f.write(content)
#         #         print(f"Transcript saved to {transcript_filename}")
#         # else:
#         #     print("No transcripts found for this meeting.")
#
#         # Process transcript using the processing API and apply fuzzy matching
#         final_items, mom_data = process_transcript("MOMTesting.vtt", attendees)
#
#         meeting_record = {
#             "meeting_id": meeting_id,
#             "meeting_subject": meeting_subject,
#             "meeting_time": datetime.fromisoformat(event["start"]["dateTime"].replace('Z', '+00:00')),
#             "attendees": attendees,
#             "mom_data": mom_data,
#             "processed_at": datetime.now()
#         }
#         result_insert = meeting_records.insert_one(meeting_record)
#         print(f"Stored meeting data in MongoDB with ID: {result_insert.inserted_id}")
#
#         return {"mom_data": mom_data}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
# class UpdateMOMRequest(BaseModel):
#     meeting_id: str
#     mom_data: dict
#
# @app.put("/update_mom")
# def update_mom(data: UpdateMOMRequest):
#     """
#     Updates the mom_data for a given meeting record.
#     """
#     result = meeting_records.update_one(
#         {"meeting_id": data.meeting_id},
#         {"$set": {"mom_data": data.mom_data, "updated_at": datetime.now()}}
#     )
#     if result.modified_count == 0:
#         raise HTTPException(status_code=404, detail="Meeting record not found or no update performed.")
#     # Return the updated record
#     updated_record = meeting_records.find_one({"meeting_id": data.meeting_id})
#     return {"updated_record": updated_record}
#
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8002)

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




