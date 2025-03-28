import { Router } from "express";
import Meeting from "./task-by-meeting.model.js";

const router = Router();

router.post("/save-tasks-by-meeting-id", async (req, res) => {
  try {
    const { meeting_id, subject, tasks } = req.body;

    // Validate input
    if (!meeting_id || !subject || !tasks || !Array.isArray(tasks)) {
      return res.status(400).json({
        error:
          "Invalid input. Meeting ID, subject, and tasks array are required.",
      });
    }

    // Upsert the document (create if not exists, update if exists)
    const meeting = await Meeting.findOneAndUpdate(
      { meetingId: meeting_id }, // Find by meeting ID
      {
        meetingId: meeting_id,
        subject,
        $addToSet: { tasks: { $each: tasks } }, // Add tasks without duplicates
      },
      { new: true, upsert: true } // Return updated doc & create if not found
    );

    res.status(201).json({
      success: true,
      message: "Tasks saved successfully",
      data: meeting,
    });
  } catch (error) {
    console.error("Error saving tasks:", error);
    res.status(500).json({ error: error.message });
  }
});

// Route to fetch meeting details by meeting_id
router.get("/get-tasks-by-meeting-id/:meeting_id", async (req, res) => {
  try {
    const { meeting_id } = req.params;

    // Find the meeting document by meeting_id
    const meeting = await Meeting.findOne({ meetingId: meeting_id });

    if (!meeting) {
      return res
        .status(404)
        .json({ success: false, message: "Meeting not found" });
    }

    res.status(200).json({ success: true, data: meeting });
  } catch (error) {
    console.error("Error fetching tasks:", error);
    res.status(500).json({ success: false, error: error.message });
  }
});

//route to fetch allthe meetings
router.get("/get-all-tasks", async (req, res) => {
  try {
    const meetings = await Meeting.find();
    res.status(200).json({ success: true, data: meetings });
  } catch (error) {
    console.error("Error fetching meetings:", error);
    res.status(500).json({ success: false, error: error.message });
  }
});

export default router;
