// src/services/MomService.js
import { fetchTasks } from "./JiraApi";

export const sendMomToAssignees = async (momText) => {
  const tasks = await fetchTasks();
  const assignees = tasks
    .map((task) => task.fields.assignee?.emailAddress)
    .filter(Boolean);

  // Here you can call your backend service to email them
  console.log("Sending MOM to:", assignees);
  console.log("MOM Content:", momText);

  // Example: await axios.post("/send-mom", { momText, assignees });
};
