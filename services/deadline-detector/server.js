import express from "express";
import dotenv from "dotenv";
dotenv.config();
import emailRoute from "./email service/send-email-route.js";
// import detectRoute from "./detector/detector-service.js";
import taskRoute from "./jira-api-services/jira-api-service.js";
import projectRoute from "./jira-api-services/fetch-project-details.js";
import CreatetaskRoute from "./jira-api-services/create-tasks.js";
import updateRoute from "./jira-api-services/update-missing-fields.js";
import emailAutomationRoute from "./email-automation/email-automation-route.js";
import meetingRoute from "./n8n-config/meeting-routes.js";
import momRoutes from "./mom-data/mom-routes.js";
import geminiRoutes from "./gemini/gemini-routes.js";
import cors from "cors";
import connectToDatabase from "./config/dbConfig.js";

const app = express();

app.use(express.json());

app.use(cors());

app.get("/", (req, res) => {
  res.send("Deadline Detector Service");
});

app.use("/api/v1", emailRoute);

// app.use("/api/v1", detectRoute);
app.use("/api/v1", taskRoute);
app.use("/api/v1", projectRoute);
app.use("/api/v1", CreatetaskRoute);
app.use("/api/v1", updateRoute);
app.use("/api/v1", emailAutomationRoute);
app.use("/api/v1/meetings", meetingRoute);
app.use("/api/v1", momRoutes);
app.use("/api/v1/gemini", geminiRoutes);

const PORT = process.env.PORT || 3005;
app.listen(PORT, async () => {
  await connectToDatabase();
  console.log(`Server is running on:http://localhost:${PORT}`);
});
