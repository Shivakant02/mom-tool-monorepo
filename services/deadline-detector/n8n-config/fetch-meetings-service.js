import axios from "axios";

// Function to fetch upcoming events in IST
const fetchUpcomingEvents = async (accessToken) => {
  // Get the current date in IST (Indian Standard Time, UTC+5:30)
  const currentDate = new Date();
  const istOffset = 5.5 * 60 * 60 * 1000; // Convert hours to milliseconds
  const istDate = new Date(currentDate.getTime() + istOffset);
  const istDateString = istDate.toISOString(); // Convert to ISO format

  // Microsoft Graph API URL
  const graphApiUrl = `${process.env.GRAPH_API_URL}/v1.0/me/events?$filter=start/dateTime ge '${istDateString}'&$orderby=start/dateTime asc`;

  try {
    // Make the request to Microsoft Graph API
    const response = await axios.get(graphApiUrl, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        Prefer: 'outlook.timezone="Asia/Kolkata"', // Force response in IST
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
