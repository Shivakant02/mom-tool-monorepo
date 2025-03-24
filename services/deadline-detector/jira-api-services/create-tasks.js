import { Router } from "express";
import { getAccountIdByEmail, createJiraIssue } from "./jira-funtion-tasks.js";

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
          // 🔥 Add due date here if provided
          ...(due_date && { duedate: due_date }),
        },
      };

      // Create the Jira Issue with optional due date
      const response = await createJiraIssue(payload);

      if (response && response.key) {
        results.push({
          email: assignee_email,
          status: "success",
          task_id: response.key,
          due_date: due_date || "not provided",
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
