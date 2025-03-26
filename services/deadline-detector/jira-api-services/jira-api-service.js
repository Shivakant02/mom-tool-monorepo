// routes/jira.js
import express from "express";
import axios from "axios";

const router = express.Router();

router.get("/tasks", async (req, res) => {
  try {
    const { JIRA_EMAIL, JIRA_API_TOKEN, JIRA_BASE_URL, JIRA_PROJECT_KEY } =
      process.env;

    const response = await axios.get(`${JIRA_BASE_URL}/rest/api/3/search`, {
      params: {
        jql: `project=${JIRA_PROJECT_KEY} AND issuetype=Task`,
        fields: "summary,status,assignee,duedate",
      },
      headers: {
        Authorization: `Basic ${Buffer.from(
          `${JIRA_EMAIL}:${JIRA_API_TOKEN}`
        ).toString("base64")}`,
        Accept: "application/json",
      },
    });
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

export default router;
