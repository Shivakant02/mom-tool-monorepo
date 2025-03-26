// import { Router } from "express";
// import {
//   notifyAssigneeMissingFields,
//   sendDeadlineEmail,
// } from "../email service/sendgrid-service.js";

import {
  notifyAssigneeMissingFields,
  sendDeadlineEmail,
} from "../email service/sendgrid-service.js";

// const router = Router();

// const FIELDS_TO_CHECK = ["due_date", "summary", "description", "email"]; // updated fields

// router.post("/detect", async (req, res) => {
//   const tasks = req.body;

//   if (!tasks || !Array.isArray(tasks)) {
//     return res
//       .status(400)
//       .json({ error: "Invalid input. Expected an array of tasks." });
//   }

//   const results = [];

//   for (const task of tasks) {
//     const missingFields = [];

//     FIELDS_TO_CHECK.forEach((field) => {
//       if (
//         !task[field] ||
//         (typeof task[field] === "string" && task[field].trim() === "")
//       ) {
//         missingFields.push(field);
//       }
//     });

//     if (missingFields.length > 0) {
//       results.push({
//         task_id: task.task_id,
//         email: task.email || "N/A",
//         missing_fields: missingFields,
//       });

//       await sendDeadlineEmail({
//         to: "shivakant1@lumiq.ai", // Hardcoded PM or manager email
//         taskId: task.task_id,
//         missingFields,
//       });

//       if (task.email) {
//         // Send email notifications only if email exists
//         await notifyAssigneeMissingFields({
//           to: task.email,
//           taskId: task.task_id,
//           missingFields,
//         });
//       } else {
//         console.warn(
//           `⚠️ Skipping email for ${task.task_id} because no email is provided.`
//         );
//       }
//     }
//   }

//   return res.status(200).json({
//     success: true,
//     message: "Missing fields extracted and email(s) sent successfully",
//     data: results,
//   });
// });

// export default router;

// detector.js (create a helper file OR export from your existing route)

export const detectMissingFields = async (tasks) => {
  const results = [];

  const FIELDS_TO_CHECK = ["due_date", "summary", "description", "email"];

  for (const task of tasks) {
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
        email: task.email || "N/A",
        missing_fields: missingFields,
      });

      await sendDeadlineEmail({
        to: process.env.ORGANIZER_EMAIL,
        taskId: task.task_id,
        missingFields,
      });

      if (task.email) {
        await notifyAssigneeMissingFields({
          to: task.email,
          taskId: task.task_id,
          missingFields,
        });
      } else {
        console.warn(
          `⚠️ Skipping email for ${task.task_id} because no email is provided.`
        );
      }
    }
  }

  return results;
};
