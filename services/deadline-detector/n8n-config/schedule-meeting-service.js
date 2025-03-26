import axios from "axios";

const N8N_WEBHOOK_URL = `${process.env.GRAPH_API_URL}/v1.0/me/events`;
const GRAPH_API_ACCESS_TOKEN = process.env.GRAPH_API_ACCESS_TOKEN;

const scheduleMeeting = async (meetingData) => {
  try {
    if (!GRAPH_API_ACCESS_TOKEN) {
      throw new Error("GRAPH_API_ACCESS_TOKEN is missing");
    }

    const response = await axios.post(N8N_WEBHOOK_URL, meetingData, {
      headers: {
        Authorization: `Bearer ${GRAPH_API_ACCESS_TOKEN}`,
        "Content-Type": "application/json",
      },
    });

    return response.data;
  } catch (error) {
    throw new Error(error.response?.data || error.message);
  }
};

export default scheduleMeeting;
