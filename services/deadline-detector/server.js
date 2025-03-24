import express from "express";
import dotenv from "dotenv";
dotenv.config();
import emailRoute from "./email service/send-email-route.js";
// import detectRoute from "./detector/detector-service.js";
import taskRoute from "./jira-api-services/jira-api-service.js";
import projectRoute from "./jira-api-services/fetch-project-details.js";
import CreatetaskRoute from "./jira-api-services/create-tasks.js";
import cors from "cors";

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
app.listen(3005, () => {
  console.log("Server is running on port 3005");
});
