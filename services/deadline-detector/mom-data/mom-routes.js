import { Router } from "express";
import axios from "axios";
import MoM from "./mom.model.js";

const router = Router();

const access_token = process.env.GRAPH_API_ACCESS_TOKEN;
const GRAPH_API_URL = "https://graph.microsoft.com/v1.0/me/onlineMeetings/";

// Function to fetch meeting subject from Microsoft Graph API
const getMeetingSubject = async (meetingId, accessToken) => {
  try {
    const response = await axios.get(`${GRAPH_API_URL}${meetingId}`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    return response.data.subject || "No Subject Available";
  } catch (error) {
    console.error(
      "Error fetching meeting subject:",
      error.response?.data || error.message
    );
    return "Unknown Subject";
  }
};

router.post("/mom", async (req, res) => {
  try {
    const { meeting_id, event_id, mom_data, attendees } = req.body;
    const subject = await getMeetingSubject(meeting_id, access_token); // Fetch the subject using meeting_id

    const newMoM = new MoM({
      meeting_id,
      event_id,
      subject, // Use subject fetched from API
      mom_data,
      attendees,
    });

    await newMoM.save();
    res.status(201).json({ success: true, message: "MoM saved successfully" });
  } catch (error) {
    console.error("❌ Error saving MoM:", error.message);
    res.status(500).json({ error: error.message });
  }
});

// Retrieve MoM by meeting ID
router.get("/mom/:meeting_id", async (req, res) => {
  try {
    const meeting_id = req.params.meeting_id;
    const momEntry = await MoM.findOne({ meeting_id });

    if (!momEntry) {
      return res.status(404).json({ message: "Meeting ID not found" });
    }

    res.status(200).json(momEntry);
  } catch (error) {
    console.error("❌ Error retrieving MoM:", error.message);
    res.status(500).json({ error: error.message });
  }
});

// Get all MoM entries
router.get("/mom", async (req, res) => {
  try {
    const momEntries = await MoM.find();
    res.status(200).json(momEntries);
  } catch (error) {
    console.error("❌ Error retrieving all MoM entries:", error.message);
    res.status(500).json({ error: error.message });
  }
});

export default router;
