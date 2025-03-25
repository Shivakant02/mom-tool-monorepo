import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_JIRA_API_BASE_URL; // Load from .env

export const fetchTasks = async () => {
  const response = await axios.get(`${API_BASE_URL}/api/v1/tasks`);
  console.log(response.data);
  return response.data.issues;
};

export const fetchProjectDetails = async (projectId) => {
  const response = await axios.get(
    `${API_BASE_URL}/api/v1/project/${projectId}`
  );
  return response.data;
};
