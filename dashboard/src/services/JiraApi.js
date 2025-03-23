import axios from "axios";
export const fetchTasks = async () => {
  const response = await axios.get("http://localhost:3005/api/v1/tasks");
  console.log(response.data);
  return response.data.issues;
};

export const fetchProjectDetails = async (projectId) => {
  const response = await axios.get(
    `http://localhost:3005/api/v1/project/${projectId}`
  );
  return response.data;
};
