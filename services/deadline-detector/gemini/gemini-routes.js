import { Router } from "express";
import {
  generateFollowUpAgenda,
  getSmartSummary,
} from "./smart-summery-service.js";

const router = Router();

router.post("/generate-summary", async (req, res) => {
  try {
    const momData = req.body;

    // Check if momData is empty
    if (!momData || Object.keys(momData).length === 0) {
      return res
        .status(400)
        .json({ error: "MOM data is required in request body." });
    }

    // console.log("Received MOM data:", momData);

    const summary = await getSmartSummary(momData);
    res.json({ summary });
  } catch (error) {
    console.error("Error generating summary:", error);
    res
      .status(500)
      .json({ error: "Failed to generate summary. Please try again." });
  }
});

router.post("/generate-agenda", async (req, res) => {
  try {
    const momData = req.body;

    if (!momData || Object.keys(momData).length === 0) {
      return res
        .status(400)
        .json({ error: "MOM data is required in request body." });
    }

    // console.log("Received MOM data:", momData);

    const agenda = await generateFollowUpAgenda(momData);
    res.json({ agenda });
  } catch (error) {
    console.error("Error generating agenda:", error);
    res
      .status(500)
      .json({ error: "Failed to generate agenda. Please try again." });
  }
});

export default router;
