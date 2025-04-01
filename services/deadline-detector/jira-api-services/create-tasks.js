import { Router } from "express";
import axios from "axios"; // Import Axios
import { getAccountIdByEmail, createJiraIssue } from "./jira-funtion-tasks.js";
import { detectMissingFields } from "../detector/detector-service.js";

const router = Router();
const access_token = process.env.GRAPH_API_ACCESS_TOKEN;
const GRAPH_API_URL = "https://graph.microsoft.com/v1.0/me/onlineMeetings/";

// Function to fetch meeting subject from Microsoft Graph API
const getMeetingSubject = async (meetingId, accessToken) => {
  try {
    const response = await axios.get(`${GRAPH_API_URL}${meetingId}`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    return response.data.subject || "No Subject Available";
  } catch (error) {
    console.error(
      "Error fetching meeting subject:",
      error.response?.data || error.message
    );
    return "Unknown Subject";
  }
};

// Function to save tasks by meeting_id
const saveTasksByMeeting = async (meeting_id, subject, tasks) => {
  try {
    const response = await axios.post(
      "http://localhost:3005/api/v1/save-tasks-by-meeting-id",
      {
        meeting_id,
        subject,
        tasks,
      }
    );

    return response.data;
  } catch (error) {
    console.error(
      "Error saving tasks by meeting:",
      error.response?.data || error.message
    );
  }
};

const getExistingTasksByMeetingId = async (meetingId) => {
  try {
    const response = await axios.get(
      `http://localhost:3005/api/v1/get-tasks-by-meeting-id/${meetingId}`
    );
    return response.data.tasks || []; // Ensure it returns an array of existing tasks
  } catch (error) {
    console.error(
      "Error fetching existing tasks for meeting:",
      error.response?.data || error.message
    );
    return []; // Return an empty array if an error occurs
  }
};

router.post("/create-tasks", async (req, res) => {
  const { tasks, meeting_id } = req.body; // Ensure access_token is sent

  if (!Array.isArray(tasks)) {
    return res
      .status(400)
      .json({ error: "Invalid input. Expected an array of tasks." });
  }

  // Check if meeting_id is provided
  if (!meeting_id) {
    return res.status(400).json({ error: "Meeting ID is required." });
  }
  // Fetch existing tasks for the meeting_id
  const existingTasks = await getExistingTasksByMeetingId(meeting_id);

  if (existingTasks.length > 0) {
    return res.status(400).json({
      error: "Tasks already exist for this meeting ID.",
      existingTasks,
    });
  }

  try {
    // Fetch meeting subject from Microsoft Graph API
    const subject = await getMeetingSubject(meeting_id, access_token);

    const results = [];

    for (const task of tasks) {
      const { summary, description, assignee_email, due_date } = task;

      const accountId = await getAccountIdByEmail(assignee_email);

      if (!accountId) {
        results.push({
          email: assignee_email,
          status: "failed",
          reason: "Invalid or unrecognized email",
        });
        continue;
      }

      const payload = {
        fields: {
          project: { key: process.env.JIRA_PROJECT_KEY },
          summary: summary || "No Summary Provided",
          description: {
            type: "doc",
            version: 1,
            content: [
              {
                type: "paragraph",
                content: [
                  { type: "text", text: description || "No Description" },
                ],
              },
            ],
          },
          issuetype: { name: "Task" },
          assignee: { accountId },
          ...(due_date && { duedate: due_date }),
        },
      };

      const response = await createJiraIssue(payload);

      if (response && response.key) {
        results.push({
          email: assignee_email,
          status: "success",
          task_id: response.key,
          due_date: due_date || "",
          description: description || "",
          summary: summary || "",
        });
      }
    }

    // Run missing fields detection
    const detectorResults = await detectMissingFields(results);

    // Collect Jira Task IDs
    const jiraTaskIds = results
      .filter((task) => task.status === "success")
      .map((task) => task.task_id);

    // Save tasks by meeting_id
    const saveResponse = await saveTasksByMeeting(
      meeting_id,
      subject,
      jiraTaskIds
    );

    return res.status(201).json({
      success: true,
      message: "Task processing + detection completed",
      results,
      detectorResults,
      saveResponse,
    });
  } catch (err) {
    console.error(
      "❌ Error creating tasks:",
      err.response?.data || err.message
    );
    return res
      .status(500)
      .json({ error: "Internal Server Error", details: err.message });
  }
});

export default router;
