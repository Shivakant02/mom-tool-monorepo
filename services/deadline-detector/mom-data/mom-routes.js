import { Router } from "express";
import MoM from "./mom.model.js";

const router = Router();

router.post("/mom", async (req, res) => {
  try {
    const { meeting_id, event_id, subject, mom_data, attendees } = req.body;

    const newMoM = new MoM({
      meeting_id,
      event_id,
      subject,
      mom_data,
      attendees,
    });

    await newMoM.save();
    res.status(201).json({ success: true, message: "MoM saved successfully" });
  } catch (error) {
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
    res.status(500).json({ error: error.message });
  }
});

//get all MoM
router.get("/mom", async (req, res) => {
  try {
    const momEntries = await MoM.find();
    res.status(200).json(momEntries);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;
