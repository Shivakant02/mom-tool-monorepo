import { Router } from "express";
import { sendDeadlineEmail } from "./sendgrid-service.js";

const router = Router();

router.post("/send-email", async (req, res) => {
  const { to, taskId, missingFields, cc = [] } = req.body;

  if (!to || !taskId || !missingFields || !Array.isArray(missingFields)) {
    return res.status(400).json({
      message: "Missing required fields: to, taskId, or missingFields",
    });
  }

  try {
    await sendDeadlineEmail({
      to,
      taskId,
      missingFields,
      cc,
    });

    res.status(200).json({
      success: true,
      message: "✅ Email sent successfully",
    });
  } catch (error) {
    console.error("❌ Error sending email:", error.message);
    res.status(500).json({ message: "❌ Failed to send email" });
  }
});

export default router;
