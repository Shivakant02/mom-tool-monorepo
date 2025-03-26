import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_JIRA_API_BASE_URL;
const API_URL = `${API_BASE_URL}/api/v1/meetings/schedule-meeting`;

export const scheduleMeeting = async (meetingData) => {
  try {
    const response = await axios.post(API_URL, meetingData, {
      headers: {
        "Content-Type": "application/json",
      },
    });
    return response.data;
  } catch (error) {
    console.error(
      "Error scheduling meeting:",
      error.response?.data || error.message
    );
    throw new Error(
      error.response?.data?.error || "Failed to schedule meeting"
    );
  }
};
