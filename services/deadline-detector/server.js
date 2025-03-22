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

app.use("/api/v1", emailRoute);

app.use("/api/v1", detectRoute);
app.listen(3001, () => {
  console.log("Server is running on port 3001");
});
