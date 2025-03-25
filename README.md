# Automated MoM Generation and Action Tracking from MS Teams Meetings

## Project Overview

This project automates the entire process of generating Minutes of Meeting (MoM) from MS Teams meetings. It extracts key discussion points, identifies action items, and seamlessly integrates with Jira for task creation and tracking. Additionally, it automates MoM distribution and provides a dashboard for team leads to monitor tasks and updates.

## How It Works

### 1. Meeting Recording & Transcription

- The MS Teams meeting is recorded.
- The recording is processed to generate a transcript.

### 2. MoM Generation & Action Item Extraction

- The transcript is analyzed to extract key discussion points.
- A well-structured MoM is generated, including action items.
- Extracted action items include:
  - **Summary of the task**
  - **Description of the task**
  - **Assignee Email** (who is responsible)
  - **Due Date** (deadline for the task)
- All extracted data is structured in JSON format.

### 3. Automated Jira Task Creation

- Using Jira’s API, tasks are created automatically based on action items.
- If the assignee email or due date is missing, an email is triggered to the project lead requesting an update.

### 4. Automated Email Distribution

- The generated MoM is sent to all meeting attendees via email.
- The MoM is attached in PDF format for reference.

### 5. Dashboard for Team Leads

- A dashboard is provided where team leads can:
  - Monitor task updates from Jira.
  - Track the status of all action items.
  - View MoM details in an organized way.

## Key Benefits

- **Eliminates manual effort** in MoM creation.
- **Ensures all action items are tracked and assigned properly**.
- **Automates Jira task creation** and project tracking.
- **Provides real-time insights** to project leads via a dashboard.

## Technologies Used

- **Microsoft Teams API** for meeting recording and transcription.
- **Jira API** for automated task creation.
- **Email Automation** for distributing MoM.
- **Dashboard (Web Application)** for tracking action items.

## Installation & Setup

1. Clone the repository:
   git clone https://github.com/your-repo/automated-mom.git

2. Install dependencies:
   pip install -r requirements.txt

3. Configure API keys and credentials for Microsoft Teams, Jira, and email services in `.env`.
4. Run this application on termial 1:
   Download the file :mom_aut.tar
   Run the command:
   docker run -d -p 8001:8001 shivakant02/mom_auto

5. Run this application on termial 2:
   Download the file :mom_aut.tar
   Run the command:
   docker run -p 3005:3005 --env-file .env shivakant02/deadline-detector
   docker run -d -p 3005:3005 \
   -e SENDGRID_KEY="YOUR_SENDGRID_KEY" \
   -e SENDGRID_FROM_EMAIL="your_email@example.com" \
   -e FRONTEND_URL="http://your-frontend-url" \
   -e JIRA_URL="https://your-jira-url" \
   -e JIRA_EMAIL="your_jira_email@example.com" \
   -e JIRA_API_TOKEN="YOUR_JIRA_API_TOKEN" \
   -e JIRA_PROJECT_KEY="YOUR_PROJECT_KEY" \
   deadline-detector

   docker run -p 8080:80 --env-file .env shivakant02/react-vite-frontend
   docker run -p 8080:80 \
   -e VITE_JIRA_API_BASE_URL="http://dynamic-api.com" \
   -e VITE_MOM_API_BASE_URL="http://dynamic-mom.com" \
   -e VITE_PROJECT_KEY="DYNAMIC_CPG" \
   react-vite-frontend
