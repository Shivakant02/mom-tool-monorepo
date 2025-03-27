import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_JIRA_API_BASE_URL;
const API_URL = `${API_BASE_URL}/api/v1/meetings/upcoming-events`;
export const upcomingEvents = async () => {
  try {
    const response = await axios.get(API_URL, {
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = response.data;
    return data.events.map((event) => ({
      subject: event.subject,
      startTime: event.start.dateTime,
      endTime: event.end.dateTime,
      organizer: event.organizer.emailAddress.address,
      attendees: event.attendees.map((a) => a.emailAddress.address),
      joinUrl: event.onlineMeeting?.joinUrl || "#",
    }));
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

//past events
const PAST_EVENTS_URL = `${API_BASE_URL}/api/v1/meetings/past-events`;
export const pastEvents = async () => {
  try {
    const response = await axios.get(PAST_EVENTS_URL, {
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = response.data;
    return data.events.map((event) => ({
      subject: event.subject,
      startTime: event.start.dateTime,
      endTime: event.end.dateTime,
      organizer: event.organizer.emailAddress.address,
      attendees: event.attendees.map((a) => a.emailAddress.address),
      joinUrl: event.onlineMeeting?.joinUrl || "#",
    }));
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
