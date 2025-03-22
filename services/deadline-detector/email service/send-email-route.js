import { Router } from "express";
import { sendDeadlineEmail } from "./sendgrid-service.js";

const router = Router();

router.post("/send-email", async (req, res) => {
  const { to, from, taskName, deadline, taskId, cc = [] } = req.body;
  try {
    await sendDeadlineEmail({ to, from, taskName, deadline, taskId, cc });
    res.status(200).send("Email sent successfully");
  } catch (error) {
    res.status(500).send("Failed to send email");
  }
});

export default router;
