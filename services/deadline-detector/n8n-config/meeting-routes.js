import { Router } from "express";
import scheduleMeeting from "./schedule-meeting-service.js";
import fetchUpcomingEvents from "./fetch-meetings-service.js";
import fetchPastEvents from "./fetch-past-events-service.js";
import fetchAllUsers from "./fetch-user-service.js";

const router = Router();
const access_token = process.env.GRAPH_API_ACCESS_TOKEN;

router.post("/schedule-meeting", async (req, res) => {
  try {
    const meetingData = req.body;

    const result = await scheduleMeeting(meetingData);
    res.status(200).json({
      success: true,
      message: "Meeting scheduled successfully",
      data: result,
    });
  } catch (error) {
    res
      .status(500)
      .json({ error: "Failed to schedule meeting", details: error.message });
  }
});

// Endpoint to fetch upcoming events
router.get("/upcoming-events", async (req, res) => {
  try {
    const accessToken = access_token;
    if (!accessToken) {
      return res.status(400).json({ error: "Access token is missing" });
    }

    // Call the service to fetch upcoming events
    const events = await fetchUpcomingEvents(accessToken);
    res.status(200).json({ success: true, events });
  } catch (error) {
    res.status(500).json({
      error: "Failed to fetch upcoming events",
      details: error.message,
    });
  }
});

// Endpoint to fetch past events
router.get("/past-events", async (req, res) => {
  try {
    const accessToken = access_token;
    if (!accessToken) {
      return res.status(400).json({ error: "Access token is missing" });
    }

    // Call the service to fetch past events
    const events = await fetchPastEvents(accessToken);
    res.status(200).json({ success: true, events });
  } catch (error) {
    res
      .status(500)
      .json({ error: "Failed to fetch past events", details: error.message });
  }
});

router.get("/fetch-users", async (req, res) => {
  try {
    const users = await fetchAllUsers(access_token);
    res.status(200).json({
      success: true,
      message: "Users fetched successfully",
      data: users,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: "Failed to fetch users",
      details: error.message,
    });
  }
});

export default router;
