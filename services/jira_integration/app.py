import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# Load environment variables
load_dotenv()
JIRA_URL = os.getenv("JIRA_URL")
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
        return response.json()[0]["accountId"]
    return None

# Function to create Jira task
def create_jira_task(task):
    summary = task.get("summary")
    description = task.get("description")
    assignee_email = task.get("assignee_email")
    due_date = task.get("due_date")

    assignee_id = get_jira_account_id(assignee_email)
    if not assignee_id:
        return {"error": f"Invalid Assignee: {assignee_email}"}, 400

    data = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]
            },
            "issuetype": {"name": "Task"},
            "assignee": {"accountId": assignee_id}
        }
    }

    response = requests.post(f"{JIRA_URL}/rest/api/3/issue", auth=AUTH, headers=HEADERS, data=json.dumps(data))
    if response.status_code == 201:
        issue_key = response.json().get("key")
        if due_date:
            try:
                formatted_due_date = datetime.strptime(due_date, "%Y-%m-%d").strftime("%Y-%m-%d")
                update_due_date(issue_key, formatted_due_date)
            except ValueError:
                return {"error": "Invalid Due Date format. Use YYYY-MM-DD"}, 400
        return {"message": "Jira Task Created", "issue_key": issue_key}, 201
    return {"error": "Failed to create Jira task", "details": response.json()}, response.status_code

# Function to update due date
def update_due_date(issue_key, due_date):
    update_data = {"fields": {"duedate": due_date}}
    update_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}"
    requests.put(update_url, auth=AUTH, headers=HEADERS, data=json.dumps(update_data))

@app.route("/create_tasks", methods=["POST"])
def create_tasks():
    task_list = request.json.get("tasks", [])
    results = [create_jira_task(task) for task in task_list]
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)


# JSON Format 

# This is for postman testintg 
# {
#   "tasks": [
#     {
#       "summary": "Follow up on budget approval",
#       "description": "Ensure the finance team reviews the budget proposal.",
#       "assignee_email": "shivakant1@lumiq.ai",
#       "due_date": "2025-03-30"
#     },
#     {
#       "summary": "Prepare project presentation",
#       "description": "Create a PowerPoint for the project kickoff meeting.",
#       "assignee_email": "k.pavan@lumiq.ai",
#       "due_date": ""
#     }
#   ]
# }

