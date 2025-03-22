import { Router } from "express";
import {
  notifyAssigneeMissingFields,
  sendDeadlineEmail,
} from "../email service/sendgrid-service.js";
const router = Router();

const FIELDS_TO_CHECK = ["deadline", "summary", "priority"]; // Add more if needed

router.post("/detect", (req, res) => {
  const tasks = req.body.tasks;

  if (!tasks || !Array.isArray(tasks)) {
    return res
      .status(400)
      .json({ error: "Invalid input. 'tasks' should be an array." });
  }

  const results = [];

  tasks.forEach(async (task) => {
    const missingFields = [];

    FIELDS_TO_CHECK.forEach((field) => {
      if (
        !task[field] ||
        (typeof task[field] === "string" && task[field].trim() === "")
      ) {
        missingFields.push(field);
      }
    });

    if (missingFields.length > 0) {
      results.push({
        task_id: task.task_id,
        assigned_to: task.assigned_to,
        missing_fields: missingFields,
      });

      // Send email to the assigned person
      await sendDeadlineEmail({
        to: "kants6397@gmail.com",
        taskId: task.task_id,
        missingFields,
        cc: [task.assigned_to],
      });

      await notifyAssigneeMissingFields({
        to: task.assigned_to,
        taskId: task.task_id,
        missingFields,
      });
    }
  });

  return res.status(200).json({
    success: true,
    message: "missing fields extracted and email sent successfully",
    data: results,
  });
});

export default router;
