import axios from "axios";

// Replace this with your actual Graph API URL
const GRAPH_API_URL = process.env.GRAPH_API_URL;

const fetchAllUsers = async (accessToken) => {
  try {
    if (!accessToken) {
      throw new Error("GRAPH_API_ACCESS_TOKEN is missing");
    }

    // Fetch the users from the Microsoft Graph API
    const response = await axios.get(`${GRAPH_API_URL}/v1.0/users`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    });

    // Return an array of objects with only displayName and mail
    return response.data.value.map((user) => ({
      displayName: user.displayName,
      mail: user.mail,
    }));
  } catch (error) {
    throw new Error(error.response?.data || error.message);
  }
};

export default fetchAllUsers;
