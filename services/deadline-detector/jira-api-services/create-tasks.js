import { Router } from "express";
import { getAccountIdByEmail, createJiraIssue } from "./jira-funtion-tasks.js";
import { detectMissingFields } from "../detector/detector-service.js";

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

    // 🟢 Directly call detector logic here:
    const detectorResults = await detectMissingFields(results);

    return res.status(201).json({
      success: true,
      message: "Task processing + detection completed",
      results,
      detectorResults,
    });
  } catch (err) {
    console.error("❌ Error creating tasks:", err.message);
    return res
      .status(500)
      .json({ error: "Internal Server Error", details: err.message });
  }
});

export default router;
