import { Router } from "express";
import {
  getAccountIdByEmail,
  createJiraIssue,
  updateDueDate,
} from "./jira-funtion-tasks.js";

const router = Router();

router.post("/create-tasks", async (req, res) => {
  const tasks = req.body;

  if (!Array.isArray(tasks)) {
    return res
      .status(400)
      .json({ error: "Invalid input. Expected an array of tasks." });
  }

  try {
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
          summary: summary,
          description: {
            type: "doc",
            version: 1,
            content: [
              {
                type: "paragraph",
                content: [{ type: "text", text: description || "" }],
              },
            ],
          },
          issuetype: { name: "Task" },
          assignee: { accountId },
        },
      };

      // Step 1: Create the Jira Issue
      const response = await createJiraIssue(payload);

      if (response && response.key) {
        const issueKey = response.key;

        // Step 2: Update due date separately if provided
        if (due_date) {
          try {
            await updateDueDate(issueKey, due_date);
          } catch (err) {
            console.error(
              `❌ Failed to update due date for ${issueKey}:`,
              err.message
            );
          }
        }

        results.push({
          email: assignee_email,
          status: "success",
          task_id: issueKey,
        });
      } else {
        results.push({
          email: assignee_email,
          status: "failed",
          reason: "Task creation failed",
        });
      }
    }

    return res
      .status(201)
      .json({ message: "Task processing completed", results });
  } catch (err) {
    console.error("❌ Error creating tasks:", err.message);
    return res
      .status(500)
      .json({ error: "Internal Server Error", details: err.message });
  }
});

export default router;
