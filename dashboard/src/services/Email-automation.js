import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_JIRA_API_BASE_URL;
const API_URL = `${API_BASE_URL}/api/v1/send-mail-to-assignee`;

export const sendReminder = async (issues) => {
  if (!issues || issues.length === 0) return; // Ensure issues array is not empty

  try {
    const response = await axios.post(
      API_URL,
      { issues } // Send issues as an array
    );
    return response.data;
  } catch (error) {
    console.error(
      "Error sending reminder:",
      error.response?.data || error.message
    );
    throw new Error(error.response?.data?.error || "Failed to send reminder");
  }
};
