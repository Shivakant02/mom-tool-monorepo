import { Router } from "express";
import { updateJiraIssue } from "./jira-funtion-tasks.js";

const router = Router();

router.post("/update-missing-fields/:issueKey", async (req, res) => {
  try {
    const { fieldsToUpdate } = req.body;
    const { issueKey } = req.params;
    const response = await updateJiraIssue(issueKey, fieldsToUpdate);
    res.send(response);
  } catch (error) {
    res.status(400).send(error);
  }
});

export default router;
