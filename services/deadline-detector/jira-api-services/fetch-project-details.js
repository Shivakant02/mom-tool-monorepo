// routes/jiraRoutes.js (or wherever you define routes)
import express from "express";
import axios from "axios";
const router = express.Router();

router.get("/project/:id", async (req, res) => {
  try {
    const { JIRA_EMAIL, JIRA_API_TOKEN } = process.env;
    const { id } = req.params;

    const response = await axios.get(
      `https://lumiq-team-s5qytjpk.atlassian.net/rest/api/3/project/${id}`,
      {
        headers: {
          Authorization: `Basic ${Buffer.from(
            `${JIRA_EMAIL}:${JIRA_API_TOKEN}`
          ).toString("base64")}`,
          Accept: "application/json",
        },
      }
    );
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

export default router;
