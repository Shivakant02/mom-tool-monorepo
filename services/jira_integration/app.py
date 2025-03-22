import requests
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
JIRA_URL = os.getenv("JIRA_URL")  # Example: https://yourcompany.atlassian.net
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

# Jira API authentication
AUTH = (JIRA_EMAIL, JIRA_API_TOKEN)
HEADERS = {"Content-Type": "application/json"}

app = Flask(__name__)

# Function to fetch Jira account ID using email
def get_jira_account_id(email):
    url = f"{JIRA_URL}/rest/api/3/user/search?query={email}"
    response = requests.get(url, auth=AUTH, headers=HEADERS)

    if response.status_code == 200 and response.json():
        return response.json()[0]["accountId"]  # Return the first matched account ID
    else:
        print(f"❌ Error: Could not find Jira account for email {email}")
        return None

# Function to create Jira tasks with unique details for each task
def create_jira_tasks(task_list):
    results = []

    for task in task_list:
        summary = task.get("summary")
        description = task.get("description")
        assignee_email = task.get("assignee_email")
        due_date = task.get("due_date")

        assignee_id = get_jira_account_id(assignee_email)
        
        if not assignee_id:
            print(f"⚠️ Skipping task creation for {assignee_email} (Invalid Assignee)")
            results.append({"email": assignee_email, "status": "failed", "reason": "Invalid email"})
            continue  # Skip this task if the assignee email is invalid

        data = {
            "fields": {
                "project": {"key": JIRA_PROJECT_KEY},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": description
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {"name": "Task"},
                "assignee": {"accountId": assignee_id}  # Assign the user
            }
        }

        # Create Jira Task
        response = requests.post(f"{JIRA_URL}/rest/api/3/issue", auth=AUTH, headers=HEADERS, data=json.dumps(data))

        if response.status_code == 201:
            issue_key = response.json().get("key")
            print(f"✅ Jira Task Created: {issue_key} for {assignee_email}")

            # Update Due Date Separately (if provided)
            if due_date:
                try:
                    formatted_due_date = datetime.strptime(due_date, "%Y-%m-%d").strftime("%Y-%m-%d")
                    update_due_date(issue_key, formatted_due_date)
                except ValueError:
                    print(f"❌ Error: Invalid Due Date format '{due_date}', expected YYYY-MM-DD")

            results.append({"email": assignee_email, "status": "success", "task_id": issue_key})
        else:
            print(f"❌ Error creating Jira task for {assignee_email}: {response.json()}")
            results.append({"email": assignee_email, "status": "failed", "reason": response.json()})

    return results

# Function to update due date
def update_due_date(issue_key, due_date):
    update_data = {"fields": {"duedate": due_date}}
    update_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}"

    response = requests.put(update_url, auth=AUTH, headers=HEADERS, data=json.dumps(update_data))

    if response.status_code == 204:
        print(f"✅ Due Date Updated to {due_date} for {issue_key}")
    else:
        print(f"❌ Error updating Due Date: {response.json()}")

# API Endpoint to Create Jira Tasks
@app.route("/create-tasks", methods=["POST"])
def create_tasks_api():
    data = request.json  # Expecting JSON input
    if not isinstance(data, list):
        return jsonify({"error": "Invalid input. Expected a list of tasks"}), 400

    result = create_jira_tasks(data)
    return jsonify({"message": "Task processing completed", "results": result})

if __name__ == "__main__":
    app.run(debug=True)

