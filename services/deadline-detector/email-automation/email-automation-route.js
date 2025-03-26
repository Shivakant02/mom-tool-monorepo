import { Router } from "express";
import sendReminderEmails from "./email-automation-service.js";

const router = Router();

// Route to send reminders
router.post("/send-mail-to-assignee", async (req, res) => {
  const { issues } = req.body;

  const result = await sendReminderEmails(issues);

  if (result.success) {
    return res.status(200).json(result);
  } else {
    return res.status(500).json(result);
  }
});

export default router;
