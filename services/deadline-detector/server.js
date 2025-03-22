import express from "express";
import dotenv from "dotenv";
dotenv.config();
import emailRoute from "./email service/send-email-route.js";
import detectRoute from "./detector/detector-service.js";

const app = express();

app.use(express.json());

app.get("/", (req, res) => {
  res.send("Deadline Detector Service");
});

// await sendDeadlineEmail({
//   to: "kants6397@gmail.com",
//   from: "shivakant52@nitmanipur.ac.in",
//   taskName: "Prepare Quarterly Report",
//   deadline: "2025-03-20",
//   taskId: "TASK-101",
//   cc: ["emimicshiva11@gmail.com", "manager@example.com"],
// });

app.use("/api/v1", emailRoute);

app.use("/api/v1", detectRoute);
app.listen(3001, () => {
  console.log("Server is running on port 3001");
});
