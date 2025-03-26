import axios from "axios";

// Function to fetch past events
const fetchPastEvents = async (accessToken) => {
  // Get the current date in ISO format
  const currentDate = new Date().toISOString();

  // Graph API URL to fetch events that ended before the current date
  const graphApiUrl = `${process.env.GRAPH_API_URL}/v1.0/me/events?$filter=end/dateTime le '${currentDate}'&$orderby=end/dateTime desc`;

  try {
    // Make the request to Microsoft Graph API
    const response = await axios.get(graphApiUrl, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    // Return the list of past events
    return response.data.value;
  } catch (error) {
    // Handle error
    console.error(
      "Error fetching past events:",
      error.response ? error.response.data : error.message
    );
    throw new Error("Failed to fetch past events");
  }
};

export default fetchPastEvents;
