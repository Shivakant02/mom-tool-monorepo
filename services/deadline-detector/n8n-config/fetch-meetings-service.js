import axios from "axios";

// Function to fetch upcoming events
const fetchUpcomingEvents = async (accessToken) => {
  // Get the current date in ISO format
  const currentDate = new Date().toISOString();

  // Graph API URL to fetch events that start from the current date onward
  const graphApiUrl = `${process.env.GRAPH_API_URL}/v1.0/me/events?$filter=start/dateTime ge '${currentDate}'&$orderby=start/dateTime asc`;

  try {
    // Make the request to Microsoft Graph API
    const response = await axios.get(graphApiUrl, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    // Return the list of upcoming events
    return response.data.value;
  } catch (error) {
    // Handle error
    console.error(
      "Error fetching upcoming events:",
      error.response ? error.response.data : error.message
    );
    throw new Error("Failed to fetch upcoming events");
  }
};

export default fetchUpcomingEvents;
